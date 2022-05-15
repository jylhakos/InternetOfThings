package getenv

import (
    "log"

    "github.com/spf13/viper"
)

const project = "web"

func GetEnvVar(key string) string {

    viper.SetConfigFile(".env")

    err := viper.ReadInConfig()

    if err != nil {
        log.Fatalf("Error loading .env file %s", err)
    }

    value, _ := viper.Get(key).(string)

    return value
}