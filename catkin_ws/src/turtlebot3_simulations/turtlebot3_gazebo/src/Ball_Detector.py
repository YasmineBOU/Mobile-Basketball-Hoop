import os
import cv2
import numpy

import imutils


from pprint import pprint


# Debug variables
DEBUG = True

class Ball_Detector(object):

	"""docstring for Ball_Detector"""


	#  TO DO : Find a method that does generate this automatically for known colors
	COLOR_BOUNDARIES = {
		"green" : {
			"lower" : [29, 86, 6],
			"upper" : [64, 255, 255]
		},
		"orange" : {
			"lower" : [],
			"upper" : []
		},
		"red": {
			"lower" : [0, 0, 100],
			"upper" : [100, 100, 255]
		}
	}

	
	def __init__(self, args):
		"""
			Initializes some needed variables and calls the main function
		"""

		self.filePath 	 = args["filePath"]
		self.objectColor = args["objectColor"].lower()
		
		self.upper 		 = numpy.array(self.COLOR_BOUNDARIES[self.objectColor]["upper"], dtype = "uint8")
		self.lower 		 = numpy.array(self.COLOR_BOUNDARIES[self.objectColor]["lower"], dtype = "uint8")

		self.p1, self.p2 = None, None
		self.centerPoint = None
		self.refRadius   = 10

		self.main()




	def getBallLocation(self):
		"""
			Makes some significant transformations in order to detect the ROI
			this way, it calculates the main interesting points, mainly the 
			boundaries points and the center 
		"""

		image = cv2.imread(self.filePath)


		try:
			self.centerPoint = self.getCenterCoords(
				p1 = (0, 0), 
				p2 = image.shape[:2]
			)

			image = imutils.resize(image, width = 300)
			blur  = cv2.GaussianBlur(image, (11, 11), 0)
			hsvImg= cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)


			# mask = cv2.inRange(hsvImg, self.lower, self.upper)
			mask = cv2.inRange(blur, self.lower, self.upper)
			mask = cv2.erode(mask, None, iterations=6)
			mask = cv2.dilate(mask, None, iterations=6)

			# find contours in the mask 
			contours, _ = cv2.findContours(
				mask.copy(), 
				cv2.RETR_EXTERNAL,
				cv2.CHAIN_APPROX_SIMPLE
			)

			
			self.p1, self.p2 = self.getRectCoords(contours)
			# self.centerPoint = self.getCenterCoords(self.p1, self.p2)
			c = max(contours, key=cv2.contourArea)
			self.circleCenter, self.radius = cv2.minEnclosingCircle(c)
			


			cv2.circle(image, 
				(int(self.circleCenter[0]), int(self.circleCenter[1])), 
				int(self.radius),
				(0, 255, 255), 
				2
			)
			cv2.rectangle(image, self.p1, self.p2, (0, 255, 0))
			cv2.imwrite("TEST_OUTPUT/DetectedArea.png", image)
			
			if DEBUG:	
				print("P1, p2: ", self.p1, self.p2)
				print(self.circleCenter, self.radius)
				print(self.centerPoint)
				pprint(image.shape)
				cv2.imshow("Frame", numpy.hstack([image, blur, hsvImg]))
				cv2.waitKey(0) 



		except Exception as e:
			print("\n\n-> Error encountered !\n\t->Error: {}".format(e))
			raise e
			return


	def getRectCoords(self, contours):
		"""
			Returns the coordinates of the boundaries of the detected area

			Args:
				@contours : An array of coordinates that are included in the area

			Returning Type:
				* Tuple
		"""

		contours = contours[0].tolist()
		x = [coord[0][0] for coord in contours]
		y = [coord[0][1] for coord in contours]

		return (min(x), min(y)), (max(x), max(y))


	def getCenterCoords(self, p1, p2):
		"""
			Returns the coordinates of the center of "p1" and "p2"

			Args:
				@p1: the starting point (the top left side of the rectangle)
				@p2: the ending point (the bottom right side of the rectangle)

			Returning Type:
				* Tuple
		"""

		return (p2[0] + p1[0]) / 2,  (p2[1] + p1[1]) / 2  


	#  Function to check while testing with a virtual system
	def getBallFollowerCoords(self):
		"""
			Returns the position of the hoop (the ball's follower)

			Returning Type:
				* Tuple
		"""

		if not self.centerPoint: return None

		x, y = self.centerPoint[0], self.centerPoint[1]
		xFollower, yFollower = self.centerPoint
		step = self.radius / self.refRadius

		if self.p1[0] < x:
			xFollower -= step

		elif self.p1[0] > x:
			xFollower += step 
		# else: # p1[0] == x
		# 	xFollower = x


		if self.p1[1] < y:
			yFollower -= step

		elif self.p1[1] > y:
			yFollower += step

		# else: # p1[1] == y
		# 	yFollower = y

		return (xFollower, yFollower)

		




	def main(self):
		"""
			The main method that calls the essential functions
		"""

		self.getBallLocation()
		pprint(self.getBallFollowerCoords())

		# return self.getBallFollowerCoords()



if __name__ == "__main__":

	args = {
		"filePath"    : "TEST_DATA/redBall3.jpeg",
		"objectColor" : "red"
	}

	app = Ball_Detector(
		args
	)
