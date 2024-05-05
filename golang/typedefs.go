package main

type ElementType int

const (
	ElementTypeUnset ElementType = iota
	ElementTypeNode
	ElementTypeRel
)

type AttrT struct {
	Key              map[string]string `yaml:"key"`
	ExpandedKey      map[string]string
	OnCreate         map[string]string `yaml:"on_create"`
	ExpandedOnCreate map[string]string
	OnUpdate         map[string]string `yaml:"on_update"`
	ExpandedOnUpdate map[string]string
}

type NodeT struct {
	Label                string `yaml:"label" validate:"required"`
	Alias                string `yaml:"alias" validate:"required"`
	Mode                 string `yaml:"mode" validate:"required"`
	RelType              string `yaml:"reltype"`
	ExpandedRelTypeNodes []string
	ExpandedRelTypeDir   string
	Attr                 AttrT    `yaml:"attr"`
	Index                []string `yaml:"index"`
	ExpandedIndex        []string
	Constraint           []string `yaml:"constraint"`
	ExpandedConstraint   []string
	ExpandedElementType  ElementType
	DependsOn            map[string]interface{}
	Custom               []string `yaml:"custom"`
	ExpandedCustom       []string
}

type ModelT struct {
	Nodes    []NodeT `nodes:"constraint"`
	Rels     []NodeT `rels:"constraint"`
	AliasMap map[string]NodeT
}

type CypheringModelException struct {
	errorMessage string
}

func (e *CypheringModelException) Error() string {
	return e.errorMessage
}

func NewCypheringModelException(errorMessage string) *CypheringModelException {
	return &CypheringModelException{
		errorMessage: errorMessage,
	}
}
