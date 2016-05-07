#!/usr/bin/env python

# Structure was inspired by http://www.stuffaboutcode.com/2013/03/raspberry-pi-minecraft-snake.html

import mcpi.minecraft as minecraft
import mcpi.block as block
import time
import random

screenBottomLeft = minecraft.Vec3(-30,4,15)
screenTopRight = minecraft.Vec3(10,24,15)
playingBottomLeft = minecraft.Vec3(-30, 4, 14)
playingTopRight = minecraft.Vec3(10, 24, 14)

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
		for x in range(self.topRight.x - 1, self.bottomLeft.x + 1, -1):
			self.moveColumnLeft(x, self.bottomLeft.y + 1, self.topRight.y, self.bottomLeft.z)
		# And clear final column, until we need a new pipe
		self.mc.setBlocks(self.bottomLeft.x + 1, self.topRight.y - 1, self.topRight.z, self.bottomLeft.x + 1, self.bottomLeft.y + 1, self.topRight.z, block.AIR)
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
		self.bottomLeft = bottomLeft
		self.topRight = topRight
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
		self.mc.setBlock(self.x, self.y, self.bottomLeft.z, block.AIR)

	def draw(self):
		self.mc.setBlock(self.x, self.y, self.bottomLeft.z, block.GLOWING_OBSIDIAN)

	def detectCollision(self):
		if self.y <= self.bottomLeft.y + 1 or self.y >= self.topRight.y - 1:
			self.mc.postToChat("Hit edge of field, died.")
			return True
		elif self.mc.getBlock(self.x, self.y, self.bottomLeft.z) == block.DIAMOND_BLOCK.id:
			self.mc.postToChat("Hit pipe, died.")
			return True
		return False


def matchVec3(vec1, vec2):
	if ((vec1.x == vec2.x) and (vec1.y == vec2.y) and (vec1.z == vec2.z)):
		return True
	else:
		return False

def drawVerticalOutline(mc, x0, y0, x1, y1, z, blockType, blockData=0):
	mc.setBlocks(x0, y0, z, x0, y1, z, blockType, blockData)
	mc.setBlocks(x0, y1, z, x1, y1, z, blockType, blockData)
	mc.setBlocks(x1, y1, z, x1, y0, z, blockType, blockData)
	mc.setBlocks(x1, y0, z, x0, y0, z, blockType, blockData)

if __name__ == "__main__":
	#constants
	upControl = minecraft.Vec3(-10, 19, -9)
	middleControl = minecraft.Vec3(-10, 20, -10)

	mc = minecraft.Minecraft.create()

	# Draw an ugly board
	# Background
	mc.setBlocks(screenBottomLeft.x, screenBottomLeft.y, screenBottomLeft.z, screenTopRight.x, screenTopRight.y, screenTopRight.z, block.STONE)
	# Clear foreground
	mc.setBlocks(playingBottomLeft.x, playingBottomLeft.y, playingBottomLeft.z, playingTopRight.x, playingTopRight.y, playingTopRight.z, block.AIR)
	drawVerticalOutline(mc, playingBottomLeft.x, playingBottomLeft.y, playingTopRight.x, playingTopRight.y, playingTopRight.z, block.OBSIDIAN)

	# create control buttons
	mc.setBlock(upControl.x, upControl.y, upControl.z, block.DIAMOND_BLOCK)
	# blocks around control buttons, to stop player moving off buttons
	mc.setBlock(middleControl.x + 1,middleControl.y + 1,middleControl.z, block.GLASS)
	mc.setBlock(middleControl.x - 1,middleControl.y + 1,middleControl.z, block.GLASS)
	mc.setBlock(middleControl.x,middleControl.y + 1,middleControl.z + 2, block.GLASS)
	mc.setBlock(middleControl.x,middleControl.y + 1,middleControl.z - 1, block.GLASS)
	mc.setBlock(middleControl.x,middleControl.y - 1,middleControl.z, block.STONE)
	# put player in the middle of the control
	mc.player.setPos(middleControl.x + 0.5,middleControl.y,middleControl.z + 0,5)

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
			playerTilePos = mc.player.getTilePos()
			playerTilePos.y = playerTilePos.y - 1
			playing = bird.move(matchVec3(playerTilePos, upControl) == True) # TODO create controls, pass in whether the bird should move up
	except KeyboardInterrupt:
		print "stopped"