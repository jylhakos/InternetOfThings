package models

/*
type Album struct {
    ID     int64
    Title  string
    Artist string
    Price  float32
}
*/

type Album struct {
    ID     string  `json:"id"`
    Title  string  `json:"title"`
    Artist string  `json:"artist"`
    Price  float64 `json:"price"`
}