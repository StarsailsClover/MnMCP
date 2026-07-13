package main

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/sirupsen/logrus"
)

func main() {
	logrus.Info("Starting MnMCP Go Server...")

	r := gin.Default()

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status": "ok",
			"version": "0.1.0",
		})
	})

	// API routes
	api := r.Group("/api/v1")
	{
		api.GET("/rooms", getRooms)
		api.POST("/rooms", createRoom)
		api.POST("/bridge/connect", connectBridge)
	}

	// WebSocket endpoint
	r.GET("/ws", handleWebSocket)

	logrus.Info("Server listening on :8080")
	if err := r.Run(":8080"); err != nil {
		log.Fatal(err)
	}
}

func getRooms(c *gin.Context) {
	c.JSON(200, gin.H{
		"rooms": []gin.H{
			{
				"id":   "999999999",
				"name": "Minecraft Server",
				"host": "MnMCP Bridge",
			},
		},
	})
}

func createRoom(c *gin.Context) {
	c.JSON(201, gin.H{
		"room_id": "999999999",
		"status":  "created",
	})
}

func connectBridge(c *gin.Context) {
	c.JSON(200, gin.H{
		"status": "connected",
	})
}

func handleWebSocket(c *gin.Context) {
	// WebSocket handler
	c.String(http.StatusOK, "WebSocket endpoint")
}
