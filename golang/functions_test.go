package main

import (
	"reflect"
	"testing"
)

func TestReadYAML(t *testing.T) {
	filename := "../tests/model/test0.yaml"
	_, err := ReadYAML(filename)
	if err != nil {
		t.Errorf("Error parsing file, got %v", err)
	}
}

func TestRenderClean(t *testing.T) {
	result := RenderClean(`
	a


	b

	c`)

	expected := `
	a

	b

	c`

	if result != expected {
		t.Errorf("Expected %v, but got \n%v", expected, result)
	}
}

func TestLowerFirst(t *testing.T) {
	result := LowerFirst("CamelCase")

	expected := "camelCase"

	if !reflect.DeepEqual(result, expected) {
		t.Errorf("Expected %v, but got %v", expected, result)
	}
}

func TestExpandMap(t *testing.T) {
	container := map[string]string{"key": "${this}.one ${other}.two coalesce(${entry}.three, 'undef)'"}
	result := map[string]string{} // expanded
	depends := map[string]interface{}{}
	selfReference := "self"

	ExpandMap(container, result, depends, selfReference)

	expected := map[string]string{"key": "self.one other.two coalesce(entry.three, 'undef)'"}

	if !reflect.DeepEqual(result, expected) {
		t.Errorf("Expected %v, but got %v", expected, result)
	}
}

func TestExpandList(t *testing.T) {
	container := []string{"${this}.one ${other}.two coalesce(${entry}.three, 'undef)'"}
	result := []string{} // expanded
	depends := map[string]interface{}{}
	selfReference := "self"

	ExpandList(container, &result, depends, selfReference)

	expected := []string{"self.one other.two coalesce(entry.three, 'undef)'"}

	if !reflect.DeepEqual(result, expected) {
		t.Errorf("Expected %v, but got %v", expected, result)
	}
}

func TestExpandRelDir(t *testing.T) {
	{
		elements, direction := ExpandRelDir("a   ->   b ")
		expectedElements := []string{"a", "b"}
		expectedDirection := "->"

		if !reflect.DeepEqual(elements, expectedElements) {
			t.Errorf("Expected %v, but got %v", expectedElements, elements)
		}

		if !reflect.DeepEqual(direction, expectedDirection) {
			t.Errorf("Expected %v, but got %v", expectedDirection, direction)
		}
	}

	{
		elements, direction := ExpandRelDir("a - b")
		expectedElements := []string{"a", "b"}
		expectedDirection := "-"

		if !reflect.DeepEqual(elements, expectedElements) {
			t.Errorf("Expected %v, but got %v", expectedElements, elements)
		}

		if !reflect.DeepEqual(direction, expectedDirection) {
			t.Errorf("Expected %v, but got %v", expectedDirection, direction)
		}
	}

	{
		elements, direction := ExpandRelDir("a <- b")
		expectedElements := []string{"b", "a"}
		expectedDirection := "->"

		if !reflect.DeepEqual(elements, expectedElements) {
			t.Errorf("Expected %v, but got %v", expectedElements, elements)
		}

		if !reflect.DeepEqual(direction, expectedDirection) {
			t.Errorf("Expected %v, but got %v", expectedDirection, direction)
		}
	}
}
