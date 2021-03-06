#!/usr/bin/env python

# Structure was inspired by http://www.stuffaboutcode.com/2013/03/raspberry-pi-minecraft-snake.html

import mcpi.minecraft as minecraft
import mcpi.block as block
import time
import random

screenBottomLeft = minecraft.Vec3(-30,14,15)
screenTopRight = minecraft.Vec3(10,34,15)
playingBottomLeft = minecraft.Vec3(-30, 14, 14)
playingTopRight = minecraft.Vec3(10, 34, 14)

birdX = .4
birdStartY = .5

pipeDistance = 12
pipeGap = 5

class Field:
	def __init__(self, mc, bottomLeft, topRight):
		self.mc = mc
		self.bottomLeft = bottomLeft
		self.topRight = topRight
		self.createRandomPipe()
		self.pipeCounter = 0;

	def createRandomPipe(self):
		fieldHeight = self.topRight.y - self.bottomLeft.y
		gap = random.randrange(fieldHeight - pipeGap)
		self.createPipe(0, gap)
		self.createPipe(gap + pipeGap, fieldHeight - 1)

	def createPipe(self, start, end):
		fieldHeight = self.topRight.y - self.bottomLeft.y
		self.mc.setBlocks(self.bottomLeft.x + 1, self.topRight.y - fieldHeight + start + 1, self.topRight.z, self.bottomLeft.x + 1, self.topRight.y - fieldHeight + end, self.topRight.z, block.DIAMOND_BLOCK)

	def move(self):
		# Move everything to the left
		for x in range(self.topRight.x - 1, self.bottomLeft.x + 1, -1):
			self.moveColumnLeft(x, self.bottomLeft.y + 1, self.topRight.y, self.bottomLeft.z)
		# And clear final column, until we need a new pipe
		self.mc.setBlocks(self.bottomLeft.x + 1, self.topRight.y - 1, self.topRight.z, self.bottomLeft.x + 1, self.bottomLeft.y + 1, self.topRight.z, block.AIR)
		# Create a new pipe when we have traveled pipeDistance
		self.pipeCounter += 1
		if self.pipeCounter % pipeDistance == 0:
			self.createRandomPipe()

	def moveColumnLeft(self, x, ystart, yend, z):
		for y in range(ystart, yend):
			if not self.mc.getBlock(x - 1, y, z) == block.GLOWING_OBSIDIAN.id and not self.mc.getBlock(x, y, z) == block.GLOWING_OBSIDIAN.id:
				# don't move the bird, don't overwrite the bird
				self.mc.setBlock(x, y, z, self.mc.getBlock(x - 1, y, z))

class Bird:
	def __init__(self, mc, bottomLeft, topRight):
		self.mc = mc
		self.z = bottomLeft.z
		self.x = topRight.x + birdX * (bottomLeft.x - topRight.x)
		self.y = topRight.y + birdStartY * (bottomLeft.y - topRight.y)

	def move(self, up=False):
		self.remove()
		if up:
			self.y += 1
		else:
			self.y -= 1
		keepPlaying = not self.detectCollision()
		self.draw()
		return keepPlaying

	def remove(self):
		self.mc.setBlock(self.x, self.y, self.z, block.AIR)

	def draw(self):
		self.mc.setBlock(self.x, self.y, self.z, block.GLOWING_OBSIDIAN)

	def detectCollision(self):
		if self.mc.getBlock(self.x, self.y, self.z) == block.OBSIDIAN.id:
			self.mc.postToChat("Hit edge of field, died.")
			return True
		elif self.mc.getBlock(self.x, self.y, self.z) == block.DIAMOND_BLOCK.id:
			self.mc.postToChat("Hit pipe, died.")
			return True
		return False


def drawVerticalOutline(mc, x0, y0, x1, y1, z, blockType, blockData=0):
	mc.setBlocks(x0, y0, z, x0, y1, z, blockType, blockData)
	mc.setBlocks(x0, y1, z, x1, y1, z, blockType, blockData)
	mc.setBlocks(x1, y1, z, x1, y0, z, blockType, blockData)
	mc.setBlocks(x1, y0, z, x0, y0, z, blockType, blockData)

if __name__ == "__main__":
	mc = minecraft.Minecraft.create()

	# Draw an ugly board
	# Background
	mc.setBlocks(screenBottomLeft.x, screenBottomLeft.y, screenBottomLeft.z, screenTopRight.x, screenTopRight.y, screenTopRight.z, block.STONE)
	# Clear foreground
	mc.setBlocks(playingBottomLeft.x, playingBottomLeft.y, playingBottomLeft.z, playingTopRight.x, playingTopRight.y, playingTopRight.z, block.AIR)
	drawVerticalOutline(mc, playingBottomLeft.x, playingBottomLeft.y, playingTopRight.x, playingTopRight.y, playingTopRight.z, block.OBSIDIAN)

	# create control set
	control = minecraft.Vec3(-10, 5, -10)
	mc.setBlock(control.x,control.y,control.z, block.STONE)
	mc.setBlock(control.x,control.y + 2,control.z + 1, block.GLASS)
	mc.player.setPos(control.x+0.5,control.y+1,control.z-0.1)

	# Set up field & bird
	field = Field(mc, playingBottomLeft, playingTopRight)
	bird = Bird(mc, playingBottomLeft, playingTopRight)

	# Kick off game loop
	playing = True
	try:
		#loop until game over
		while playing == True:
			time.sleep(0.3)
			field.move()
			playing = bird.move(mc.events.pollBlockHits())
	except KeyboardInterrupt:
		print "stopped"