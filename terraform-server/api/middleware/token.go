package middleware

import (
	"fmt"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/common-lib/token"
	"github.com/WeBankPartners/wecube-plugins-terraform/terraform-server/models"
	"github.com/gin-gonic/gin"
	"net/http"
)

func GetRequestUser(c *gin.Context) string {
	user := models.AdminUser
	if models.Config.Auth.Enable {
		user = c.GetString("user")
	}
	return user
}

func GetRequestRoles(c *gin.Context) []string {
	roles := []string{models.AdminUser}
	if models.Config.Auth.Enable {
		roles = c.GetStringSlice("roles")
	}
	return roles
}

func authRequest(c *gin.Context) error {
	if !models.Config.Auth.Enable {
		return nil
	}
	authHeader := c.GetHeader("Authorization")
	if authHeader == "" {
		return fmt.Errorf("Can not find Request Header Authorization ")
	}
	authToken, err := token.DecodeJwtToken(authHeader, models.Config.Wecube.JwtSigningKey)
	if err != nil {
		return err
	}
	if authToken.User == "" {
		return fmt.Errorf("Token content is illegal,main message is empty ")
	}
	c.Set("user", authToken.User)
	c.Set("roles", authToken.Roles)
	return nil
}

func AuthCoreRequestToken() gin.HandlerFunc {
	return func(c *gin.Context) {
		err := authCoreRequest(c)
		if err != nil {
			c.JSON(http.StatusOK, models.EntityResponse{Status: "ERROR", Message: "Permission deny "})
			c.Abort()
		} else {
			c.Next()
		}
	}
}

func AuthCorePluginToken() gin.HandlerFunc {
	return func(c *gin.Context) {
		err := authCoreRequest(c)
		if err != nil {
			c.JSON(http.StatusOK, pluginInterfaceResultObj{ResultCode: "1", ResultMessage: "Token authority validate fail", Results: pluginInterfaceResultOutput{Outputs: []string{}}})
			c.Abort()
		} else {
			c.Next()
		}
	}
}

type pluginInterfaceResultObj struct {
	ResultCode    string                      `json:"resultCode"`
	ResultMessage string                      `json:"resultMessage"`
	Results       pluginInterfaceResultOutput `json:"results"`
}

type pluginInterfaceResultOutput struct {
	Outputs []string `json:"outputs"`
}

func authCoreRequest(c *gin.Context) error {
	authHeader := c.GetHeader("Authorization")
	if authHeader == "" {
		return fmt.Errorf("Can not find Request Header Authorization ")
	}
	authToken, err := token.DecodeJwtToken(authHeader, models.Config.Wecube.JwtSigningKey)
	if err != nil {
		return err
	}
	if authToken.User == "" {
		return fmt.Errorf("Token content is illegal,main message is empty ")
	}
	c.Set("user", authToken.User)
	c.Set("roles", authToken.Roles)
	return nil
}
