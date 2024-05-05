package main

import (
	"errors"
	"io/ioutil"
	"log"
	"regexp"
	"strconv"
	"strings"

	"github.com/go-playground/validator"
	"gopkg.in/yaml.v2"
)

// TODO, propagate errors back to the user (cmd)

// utilities

func ReadYAML(filename string) (*ModelT, error) {

	data, err1 := ioutil.ReadFile(filename)
	if err1 != nil {
		// TODO raise custom exception
		log.Fatalf("Failed to read file: %v", err1)
		return nil, err1
	}

	var model ModelT

	err2 := yaml.Unmarshal([]byte(data), &model)
	if err2 != nil {
		// TODO raise custom exception
		log.Fatalf("error: %v", err2)
		return nil, err2
	}

	validate := validator.New()
	err3 := validate.Struct(model)
	if err3 != nil {
		// Handle validation errors
		var validationErrors []string
		for _, e := range err3.(validator.ValidationErrors) {
			validationErrors = append(validationErrors, e.Value().(string))
		}
		errorString := strings.Join(validationErrors, "\n")
		return nil, errors.New(errorString)
	}

	return &model, nil
}

func RenderClean(text string) string {
	lines := strings.Split(text, "\n")
	cleanedLines := []string{}
	for _, line := range lines {
		if strings.TrimSpace(line) != "" {
			cleanedLines = append(cleanedLines, line)
		} else if len(cleanedLines) > 0 && strings.TrimSpace(cleanedLines[len(cleanedLines)-1]) != "" {
			cleanedLines = append(cleanedLines, line)
		}
	}
	cleanedText := strings.Join(cleanedLines, "\n")
	return cleanedText
}

// utils

func LowerFirst(strval string) string {
	return strings.ToLower(string(strval[0])) + strval[1:]
}

// expand

func ExpandMap(
	container map[string]string,
	containerExpanded map[string]string,
	dependsOn map[string]interface{},
	selfReferenceVal string,
) {
	patternVarFind := regexp.MustCompile(`(\${\w*})`)
	patternVarGet := regexp.MustCompile(`\${(\w*)}`)

	for k, v := range container {
		containerExpanded[k] = v

		for _, varReference := range patternVarFind.FindAllString(v, -1) {
			line := containerExpanded[k]

			match := patternVarGet.FindStringSubmatch(varReference)
			for i := range patternVarGet.SubexpNames() {
				varReferenceValue := match[i]

				if varReferenceValue == "this" {

					containerExpanded[k] = strings.Replace(
						line, varReference, selfReferenceVal, 1,
					)

				} else if varReferenceValue == "entry" {

					containerExpanded[k] = strings.Replace(
						line, varReference, varReferenceValue, 1,
					)

				} else {

					containerExpanded[k] = strings.Replace(
						line, varReference, varReferenceValue, 1,
					)
					dependsOn[varReferenceValue] = nil

				}
			}
		}
	}
}

func ExpandList(
	container []string,
	containerExpanded *[]string,
	dependsOn map[string]interface{},
	selfReferenceVal string,
) {
	containerMap := map[string]string{}
	expandedMap := map[string]string{}

	for i, index := range container {
		istr := strconv.Itoa(i)
		containerMap[istr] = index
	}

	ExpandMap(
		containerMap,
		expandedMap,
		dependsOn,
		selfReferenceVal,
	)

	for _, v := range expandedMap {
		*containerExpanded = append(*containerExpanded, v)
	}
}

func ExpandModel(model *ModelT) {

	// expand nodes
	ExpandNodes(model.Nodes)

	// expand rels
	ExpandRels(model.Rels)
}

func ExpandNodes(nodes []NodeT) {
	for _, node := range nodes {

		// expand attr keys
		ExpandMap(
			node.Attr.Key,
			node.Attr.ExpandedKey,
			node.DependsOn,
			node.Alias,
		)

		// expand attr on_create
		ExpandMap(
			node.Attr.OnCreate,
			node.Attr.ExpandedOnCreate,
			node.DependsOn,
			node.Alias,
		)

		// expand attr on_update
		ExpandMap(
			node.Attr.OnUpdate,
			node.Attr.ExpandedOnUpdate,
			node.DependsOn,
			node.Alias,
		)

		// expand indexes
		ExpandList(
			node.Index,
			&node.ExpandedIndex,
			node.DependsOn,
			node.Alias,
		)

		// expand constraints
		ExpandList(
			node.Constraint,
			&node.ExpandedConstraint,
			node.DependsOn,
			node.Alias,
		)

		// expand custom
		ExpandList(
			node.Custom,
			&node.ExpandedCustom,
			node.DependsOn,
			node.Alias,
		)

		node.ExpandedElementType = ElementTypeNode
	}
}

func ExpandRels(rels []NodeT) {
	ExpandNodes(rels)

	for _, rel := range rels {

		// expand rel type
		container := []string{rel.RelType}
		expanded := []string{}

		// expand custom
		ExpandList(
			container,
			&expanded,
			rel.DependsOn,
			rel.Alias,
		)

		expandedstr := strings.TrimSpace(expanded[0])

		relnodes, reldir := ExpandRelDir(expandedstr)

		rel.DependsOn[relnodes[0]] = nil
		rel.DependsOn[relnodes[1]] = nil
		rel.ExpandedRelTypeNodes = relnodes
		rel.ExpandedRelTypeDir = reldir
		rel.ExpandedElementType = ElementTypeRel
	}
}

func ExpandRelDir(strval string) ([]string, string) {
	pattern := regexp.MustCompile(`(\w*)\s*(->|-|<-)\s*(\w*)`)

	match := pattern.FindStringSubmatch(strval)
	if len(match) < 3 {
		return nil, "" // TODO raise exception
	}

	// re order the relationship
	// a -> b = same
	// b <- a = a -> b
	// b - a  = same

	node0 := match[1]
	reldir := match[2]
	node1 := match[3]

	var relnodes []string
	if reldir == "<-" {
		relnodes = []string{node1, node0}
	} else {
		relnodes = []string{node0, node1}
	}

	if reldir == "<-" {
		reldir = "->"
	}

	return relnodes, reldir
}
