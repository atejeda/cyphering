package main

type City struct {
	Name    string
	Country string
}

type Person struct {
	Name string
	Age  int
	City City
}

func main() {

	// tmpl, err := template.New("person").Parse("Hello {{.Name}}, you are {{.Age}} years old from {{ .City.Name }}!\n")
	// if err != nil {
	// 	panic(err)
	// }

	// city := City{"Rio", "Brazil"}
	// person := Person{"John", 30, city}
	// err = tmpl.Execute(os.Stdout, person)
	// if err != nil {
	// 	panic(err)
	// }
}
