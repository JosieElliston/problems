# hub: 4ft diameter, 8ft8in height

# TODO: fix 2 sided intake switching which side is used
    # something wrong with calculating predicted theta?
    # something wrong with using predicted theta?
    # use predicted position for better choice?
# TODO: use fastest path to a ball (this probably isn't the linear path)
# TODO: slow rotation to sync with path
# TODO: make rotation target be towards the ball {when the path is complete} not {right now}
# TODO: slow path to allow rotation to catch up
    # TODO: really hard: adjust path to let rotation catch up less far
# TODO: optimize which balls are chosen to 2 balls then hub (calculate path for (with optimization) all permutations of ball pairs)
# TODO: optimize which balls are chosen to n cycles
# TODO: make a path class for the robot to follow without recalculation
# TODO: refactor recalculations of MAX_DELTA_VEL and MAX_DELTA_SPEED

"""Simulates a robot, both user control and algorithmic motion.

Variables are generally in units of inches, radians, and seconds.
"""

from __future__ import annotations
import math
import random
import pygame
import pygame.gfxdraw

Point = tuple[float, float]

def to_screen(x: float, y: float) -> Point:
    """Returns the place to draw the point (x, y) in screen coords."""
    return x * SCREEN_SIZE_MULTIPLIER, y * SCREEN_SIZE_MULTIPLIER

def modulo(theta: float) -> float:
    """Returns an angle congruent to theta but in the range [-pi, pi]."""
    return (theta + math.pi) % (math.pi * 2) - math.pi

def atan(x: float, y: float) -> float:
    """Returns the angle of the point (x, y) measured from the positive x axis."""
    if x == 0:
        if y < 0:
            return -.5 * math.pi
        elif y > 0:
            return .5 * math.pi
        else:
            raise ValueError
    else:
        return modulo((math.pi * (x < 0)) + math.atan(y / x))

def length(x: float, y: float) -> float:
    """Returns the distance of the point (x, y) from the origin."""
    return (x**2 + y**2) ** .5

def normalize(x: float, y: float) -> Point:
    """Returns the projection of the point (x, y) onto the unit circle. Normalize the point."""
    magnitude = length(x, y)
    return x / magnitude, y / magnitude

def project(x: float, y: float, r: float) -> Point:
    """Returns the projection of the point (x, y) onto the unit circle scaled by r."""
    x, y = normalize(x, y)
    return x * r, y * r

def kinematic(t1: float, p0: float, v0: float, a: float) -> float:
    """Returns the updated position after the simulation"""
    return p0 + v0*t1 + (a/2) * t1**2

def square_distance(x0, y0, x1, y1) -> float:
    """Returns the distance squared between the points (x0, y0) and (x1, y1)."""
    return (x0-x1)**2 + (y0-y1)**2

def draw_angle(theta: float, length = 100) -> None:
    """Draws the line from the robot at angle theta. (For debugging)."""
    pygame.draw.aaline(screen, (250, 0, 0), to_screen(robot.x, robot.y), to_screen(robot.x + length*math.cos(theta), robot.y + length*math.sin(theta)))

def draw_vector(x: float, y: float, scale = 1) -> None:
    """Draws the line from the robot to the relative point (x, y). (For debugging)."""
    pygame.draw.aaline(screen, (250, 0, 0), to_screen(robot.x, robot.y), to_screen(robot.x + scale*x, robot.y + scale*y))

# def rotate(x, y, theta) -> Point:
# 	# rotate the point (x, y) around the origin
# 	origin = atan(x, y)
# 	mag = vec_magnitude(x, y)
# 	return mag * math.cos(origin + theta), mag * math.sin(origin + theta)

# class Triple:
# 	def __init__(self, theta, x, y) -> None:
# 		self.theta = theta
# 		self.x = x
# 		self.y = y

# class Node:
# 	def __init__(self, pos: Triple, vel: Triple, acc: Triple) -> None:
# 		self.pos, self.vel, self.acc = pos, vel, acc

# 	def eval(self, time: float) -> Triple:
# 		return self.pos + time * self.vel + .5 * self.acc ** 2

# class Path:
#     def __init__(self, robot: Robot, target: Ball) -> None:
#         self.robot = robot # this is for storing initial velocities ect.
#         self.target = target

class Ball:
    """This class represents a cargo."""

    RADIUS = 9.5

    @staticmethod
    def random() -> Point:
        """"Returns a random point on the field."""
        return random.random() * FIELD_X, random.random() * FIELD_Y

    def __init__(self) -> None:
        """Places the ball at a random point on the field"""
        self.x, self.y = Ball.random()
    
    def collect(self) -> None:
        """Randomizes the position of the ball."""
        self.x, self.y = Ball.random()
    
    def draw(self) -> None:
        """Draws the ball on the screen."""
        pygame.draw.circle(screen, (0, 0, 250), to_screen(self.x, self.y), self.RADIUS * SCREEN_SIZE_MULTIPLIER)

class Robot:
    """This class represents a robot with a swerve drive.
    
    This is an idealized swerve drive robot where individual motors aren't simulated and directional velocity is independent from linear velocity. It has maximum speed and velocity for direction and linear motion.
    """

    def __init__(self) -> None:
        """Places the robot at the middle of the field."""
        self.x: float = FIELD_X / 2
        self.y: float = FIELD_Y / 2
        self.theta: float = 0

        self.x_v: float = 0
        self.y_v: float = 0 
        self.theta_v: float = 0 
        
        self.RADIUS: float = 20
        self.MAX_LINEAR_SPEED: float = 100 # 144
        self.MAX_LINEAR_ACC: float = 500 
        self.MAX_ANGULAR_VEL: float = 2 # 5
        self.MAX_ANGULAR_ACC: float = 5
    
    def draw(self) -> None:
        def get_point(theta: float) -> Point:
            theta += self.theta
            return (self.x + (math.cos(theta) - math.sin(theta)) * self.RADIUS) * SCREEN_SIZE_MULTIPLIER, (self.y + (math.cos(theta) + math.sin(theta)) * self.RADIUS) * SCREEN_SIZE_MULTIPLIER
        points = [get_point(i * math.pi / 2) for i in range(4)] # robot vertices
        pygame.gfxdraw.filled_polygon(screen, points, (100, 100, 100)) # robot
        pygame.draw.aaline(screen, (250, 0, 0), points[0], points[3]) # front intake
        pygame.draw.aaline(screen, (250, 0, 0), points[1], points[2]) # back intake

    def update(self) -> Point:
        delta_x_v: float
        delta_y_v: float
        """Update the robot every frame, executing user or algorithmic motion.
        
        Returns the change in x and y velocity (for debugging).
        """
        self.theta = modulo(self.theta)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            target = min(balls, key = lambda ball: square_distance(self.x, self.y, ball.x, ball.y)) # target is the closest ball
            relative_x = target.x - self.x
            relative_y = target.y - self.y
            delta_theta_v = self._goto_angular(relative_x, relative_y)
            delta_x_v, delta_y_v = 0, 0
            delta_x_v, delta_y_v = self._goto_linear(relative_x, relative_y)
        else:
            if WEIRD_LAYOUT:
                controller_theta = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                controller_x = keys[pygame.K_d] - keys[pygame.K_a]
                controller_y = keys[pygame.K_s] - keys[pygame.K_w]
            else:
                controller_theta = keys[pygame.K_d] - keys[pygame.K_a]
                controller_x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                controller_y = keys[pygame.K_DOWN] - keys[pygame.K_UP]
            
            if controller_x == 0 and controller_y == 0:
                if LINEAR_RATE_MODE:
                    delta_x_v, delta_y_v = 0, 0
                else:
                    delta_x_v, delta_y_v = self._linear_dec()
            else:
                delta_x_v, delta_y_v = self._linear_acc(controller_x, controller_y)

            if controller_theta == 0:
                if ANGULAR_RATE_MODE:
                    delta_theta_v = 0
                else:
                    delta_theta_v = self._angular_dec()
            else:
                delta_theta_v = self._angular_acc(controller_theta == 1)

        # modify velocities
        self.x_v += delta_x_v
        self.y_v += delta_y_v
        self.theta_v += delta_theta_v
        
        # if linear speed goes over the maximum, scale it back
        speed = length(self.x_v, self.y_v)
        if speed > self.MAX_LINEAR_SPEED:
            scale = self.MAX_LINEAR_SPEED / speed
            self.x_v *= scale
            self.y_v *= scale
        
        # if angular velocity goes over the maximum, set it back
        if self.theta_v > self.MAX_ANGULAR_VEL:
            self.theta_v = self.MAX_ANGULAR_VEL
        elif self.theta_v < -self.MAX_ANGULAR_VEL:
            self.theta_v = -self.MAX_ANGULAR_VEL

        # modify positions
        self.x += self.x_v * (dt/1000)
        self.y += self.y_v * (dt/1000)
        self.theta += self.theta_v * (dt/1000)

        return delta_x_v, delta_y_v
    
    def _linear_acc(self, x: float, y: float) -> Point:
        """Returns the change in x and y velocity to accelerate.
        
        Accelerate at the robot's maximum linear acceleration. Accelerate towards the point (x, y), which is relative to the robot.
        """
        MAX_DELTA_SPEED = self.MAX_LINEAR_ACC * (dt/1000)
        return project(x, y, MAX_DELTA_SPEED)

    def _linear_dec(self) -> Point:
        """Returns the change in x and y velocity to decelerate.
        
        If we are able to stop motion on this frame (ie the speed is less than the usable acceleration on this frame), return values that cancel out the current motion. Otherwise, decelerate at the maximum usable acceleration.
        """
        MAX_DELTA_SPEED = self.MAX_LINEAR_ACC * (dt/1000) # maximum usable acceleration for this frame, shared between change in x and y velocity
        if length(self.x_v, self.y_v) > MAX_DELTA_SPEED:
            return self._linear_acc(-self.x_v, -self.y_v)
        else:
            return -self.x_v, -self.y_v

    def _angular_acc(self, right: bool) -> float:
        """Returns the change in theta velocity.
        
        Accelerate towards the given direction at the robot's maximum angular acceleration.
        """
        MAX_DELTA_VEL = self.MAX_ANGULAR_ACC * (dt/1000) # maximum usable acceleration for this frame
        return MAX_DELTA_VEL if right else -MAX_DELTA_VEL
        
    def _angular_dec(self) -> float:
        """Returns the change in theta velocity.
        
        If we are able to stop motion on this frame (ie the velocity is less than the usable acceleration on this frame), return a value to cancel out the current motion. Otherwise, decelerate at the maximum usable acceleration.
        """
        MAX_DELTA_VEL = self.MAX_ANGULAR_ACC * (dt/1000)
        if abs(self.theta_v) > MAX_DELTA_VEL:
            return self._angular_acc(self.theta_v < 0)
        else:
            return -self.theta_v
    
    def projected_pos(self) -> Point:
        x_dec, y_dec = normalize(self.x_v, self.y_v)
        x_dec *= -self.MAX_LINEAR_ACC
        y_dec *= -self.MAX_LINEAR_ACC
        print(x_dec, y_dec)
        time = (-self.x_v / x_dec)
        assert abs((-self.x_v / x_dec) - (-self.y_v / y_dec)) < .000001
        return kinematic(time, self.x, self.x_v, x_dec), kinematic(time, self.y, self.y_v, y_dec), 

    def projected_theta(self) -> float:
        """Returns the angle we would be at if slow down at maximum acceleration."""
        theta_dec = self.MAX_ANGULAR_ACC if self.theta_v < 0 else -self.MAX_ANGULAR_ACC # max rate at which we can slow down
        time = -self.theta_v / theta_dec # time when we hit theta_v = 0 if we decelerate at max rate
        return modulo(kinematic(time, self.theta, self.theta_v, theta_dec)) # the angle we will be when we hit 0 vel if we decelerate at max rate
    
    def _goto_linear(self, x, y) -> Point:
        """Returns the change in x and y velocities to accelerate towards the target."""
        return self._linear_acc(x, y)
        # TODO:
            # linear path
                # flip the component perpendicular to target to stop radial motion
                # use remaining acc to move towards the target
            # fastest path
                # lmao idk

    def _goto_angular(self, x, y) -> float:
        """Returns the change in theta vel to point towards the target.
        
        Begin decelerating down from max velocity at the correct time (before passing the target) to not overshoot it. If we are close to the target, return a value to get to the target ~perfectly next frame.
        """
        target = atan(x, y)
        # Check if it's better to use the back intake.
        if abs(modulo(self.projected_theta() - target)) > math.pi / 2:
            print("here")
            target = modulo(target + math.pi)
        difference = modulo(target - self.theta)
        MAX_DELTA_VEL = self.MAX_ANGULAR_ACC * (dt/1000)
        if (abs(self.theta_v) < MAX_DELTA_VEL and
                (self.theta_v - MAX_DELTA_VEL) * (dt/1000) < difference and
                difference < (self.theta_v + MAX_DELTA_VEL) * (dt/1000)):
            # if we can reach the target in 1 frame, make it such that we reach it perfectly
            return difference - self.theta_v
        elif self.theta_v == 0:
            # if we're static, accelerate in direction of the target
            return MAX_DELTA_VEL if difference > 0 else -MAX_DELTA_VEL
        else:
            # suppose we begin decelerating now, will we go past the target?
            return MAX_DELTA_VEL if modulo(self.projected_theta() - target) < 0 else -MAX_DELTA_VEL

FIELD_X = 648
FIELD_Y = 324
SCREEN_SIZE_MULTIPLIER = 2.2
FIELD_RELATIVE = True # TODO: FIX 
LINEAR_RATE_MODE = False
ANGULAR_RATE_MODE = False
WEIRD_LAYOUT = False

pygame.init()
screen = pygame.display.set_mode(to_screen(FIELD_X, FIELD_Y))
clock = pygame.time.Clock()
robot = Robot()
balls = [Ball() for i in range(5)] # 11
while not pygame.QUIT in [event.type for event in pygame.event.get()]:
    dt = clock.tick(60) # clock.tick(random.randrange(30, 60))
    screen.fill((0, 0, 0))
    delta_x_v, delta_y_v = robot.update()
    for ball in balls:
        ball.draw()
        if square_distance(robot.x, robot.y, ball.x, ball.y) < (ball.RADIUS + robot.RADIUS) ** 2:
            ball.collect()
    robot.draw()
    draw_vector(robot.x_v, robot.y_v)
    draw_vector(delta_x_v, delta_y_v)
    # pygame.draw.circle(screen, (250, 250, 250), to_screen(FIELD_X / 2, FIELD_Y / 2), 24 * SCREEN_SIZE_MULTIPLIER, width = 2) # upper hub
    # pygame.draw.circle(screen, (250, 250, 250), to_screen(FIELD_X / 2, FIELD_Y / 2), 30 * SCREEN_SIZE_MULTIPLIER, width = 2) # lower hub
    pygame.display.flip()