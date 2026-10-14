package main

import (
	"fmt"

	"github.com/xuri/excelize/v2"
)

func main() {
	f := excelize.NewFile()
	defer func() {
		if err := f.Close(); err != nil {
			fmt.Println(err)
		}
	}()
	// Create a new sheet.
	index, err := f.NewSheet("Test1")
	if err != nil {
		fmt.Println(err)
		return
	}
	// Set value of a cell.
	f.SetCellValue("Test1", "A2", "Hello world. fdsaf asdfsa fafdsaf")
	// Set active sheet of the workbook.
	f.SetColWidth("Test1", "A", "A", 100)
	// this is freeze
	if err := f.SetPanes("Test1", &excelize.Panes{
		Freeze:      true,
		Split:       false,
		XSplit:      0,    // Number of columns to freeze
		YSplit:      2,    // Number of rows to freeze
		TopLeftCell: "B3", // Cell to be the top-left of the scrollable area
	}); err != nil {
		fmt.Println(err)
		return
	}

	f.SetActiveSheet(index)
	// Save spreadsheet by the given path.
	if err := f.SaveAs("Book1.xlsx"); err != nil {
		fmt.Println(err)
	}
}
