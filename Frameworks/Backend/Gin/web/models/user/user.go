package models

import (
    "time"

    "go.mongodb.org/mongo-driver/bson/primitive"
)

type User struct {
    ID              primitive.ObjectID `bson:"_id"`
    User_id         string             `json:"user_id"`
    Name            *string            `json:"Name" validate:"required,min=2,max=100"`
    Password        *string            `json:"Password" validate:"required,min=6""`
    Email           *string            `json:"email" validate:"email,required"`
    Token           *string            `json:"token"`
    Refresh_token   *string            `json:"refresh_token"`
    Created_at      time.Time          `json:"created_at"`
    Updated_at      time.Time          `json:"updated_at"`  
}