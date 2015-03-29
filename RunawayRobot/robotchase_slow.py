# ----------
# Part Four
#
# Again, you'll track down and recover the runaway Traxbot.
# But this time, your speed will be about the same as the runaway bot.
# This may require more careful planning than you used last time.
#
# ----------
# YOUR JOB
#
# Complete the next_move function, similar to how you did last time.
#
# ----------
# GRADING
#
# Same as part 3. Again, try to catch the target in as few steps as possible.

from robot import *
from math import *
from matrix import *
import random

def next_move(hunter_position, hunter_heading, target_measurement, max_distance, OTHER = None):
    # This function will be called after each time the target moves.

    # The OTHER variable is a place for you to store any historical information about
    # the progress of the hunt (or maybe some localization information). Your return format
    # must be as follows in order to be graded properly.
    """This strategy always tries to steer the hunter directly towards where the target last
    said it was and then moves forwards at full speed. This strategy also keeps track of all
    the target measurements, hunter positions, and hunter headings over time, but it doesn't
    do anything with that information."""

        # helper function to map all angles onto [-pi, pi]
    def angle_truncate(a):
        while a < 0.0:
            a += pi * 2
        return ((a + pi) % (pi * 2)) - pi

    #print "true heading"
    #print test_target.heading
    I = matrix([[1, 0, 0],
                [0, 1, 0],
                [0, 0, 1]]) #identity matrix

    R = matrix([[measurement_noise, 0], [0, measurement_noise]])

    H = matrix([[0, 1, 0],
                [0, 0, 1]]) #Jacobian of the measurement function

    u = matrix([[0],
                [0],
                [0]])

    F = []

    heading = 0 #WILD ASS GUESS

    if OTHER is not None:
        print "-----------------"
        current_measurement = target_measurement
        last_measurement = OTHER['last_measurement']
        OTHER['measurements'].append(target_measurement)
        #I know this is stupid but I just want to save the data... Memory management be damned

        heading = atan2(target_measurement[1] - last_measurement[1], target_measurement[0] - last_measurement[0])
        print "calculated heading"
        print heading
        X = OTHER['X']
        P = OTHER['P']

        if 'last_heading' not in OTHER:
            OTHER['last_heading'] = heading
            xy_estimate = [X.value[1][0], X.value[2][0]]
            OTHER['last_measurement'] = target_measurement
        else:
            print "OTHER is:", OTHER
            turning_angle = heading - OTHER['last_heading']
            print "turning angle:", turning_angle
            print "turning angle actual:", target.turning
            #last_heading = OTHER['last_heading']


            #do some guessing
            D = distance_between(target_measurement, last_measurement)
            print "this is the D"
            print D
            theta = (heading+turning_angle)%(2*pi)
            print "theta:", theta
            print "theta - heading current:", theta - target.heading

            #estimation step

            #is it "last heading" or "theta"????
            # X = matrix([[theta],
            #             [X.value[1][0] + D * cos(theta)],
            #             [X.value[2][0] + D * sin(theta)]])

            delta_x = D * cos(theta)
            delta_y = D * sin(theta)

            nextX = target_measurement[0] + delta_x
            nextY = target_measurement[1] + delta_y

            # nextX = X.value[1][0] + delta_x
            # nextY = X.value[2][0] + delta_y

            #print "the distance to the next guessed point is:", distance_between([nextX,nextY], measurement)

            X = matrix([[theta],
                         [nextX],
                         [nextY]])

            print "I'm projecting X out to:", X
            print "Note, the current robot stats:", target.heading, target.x, target.y

            F = matrix([[1, 0, 0],
                        [-D*sin(theta), 1, 0],
                        [D*cos(theta), 0, 1]])

            P = OTHER['P']
            #X = OTHER['X']


            H = matrix([[0, 1, 0],
                        [0, 0, 1]])

            # #Prediction
            # X = (F * X) + u
            # P = F * P * F.transpose() # + Q

            P = F * P * F.transpose() # + Q

            #measurement update
            observations = matrix([[target_measurement[0]],
                         [target_measurement[1]]]) #truth
            Z = H*X
            Y = observations - Z
            print "this is Y"
            print Y
            S = H * P * H.transpose() + R
            K = P * H.transpose() * S.inverse()
            X = X + (K*Y)

            P = (I - (K * H)) * P

            X.value[0][0] = angle_truncate(X.value[0][0])


            OTHER['X'] = X

            OTHER['P'] = P
            x_estimate = OTHER['X'].value[1][0]
            y_estimate = OTHER['X'].value[2][0]
            print "Currently, the robot state is:", target.heading, observations
            print "This is what Kalman thinks X will be:", OTHER['X']
            xy_estimate = [x_estimate, y_estimate]

            OTHER['last_heading'] = heading
            OTHER['last_measurement'] = target_measurement


    else:
        #x = theta, x, y
        X = matrix([[0.5],
                    [2],
                    [4]])
        #convariance matrix
        P = matrix([[1000, 0, 0],
                    [0, 1000, 0],
                    [0, 0, 1000]])
        OTHER = {'last_measurement': target_measurement, 'X': X, 'P': P, 'measurements': [target_measurement]}
        xy_estimate = [X.value[1][0], X.value[2][0]]

    # if not OTHER: # first time calling this function, set up my OTHER variables.
    #     measurements = [target_measurement]
    #     hunter_positions = [hunter_position]
    #     hunter_headings = [hunter_heading]
    #     OTHER = (measurements, hunter_positions, hunter_headings) # now I can keep track of history
    # else: # not the first time, update my history
    #     OTHER[0].append(target_measurement)
    #     OTHER[1].append(hunter_position)
    #     OTHER[2].append(hunter_heading)
    #     measurements, hunter_positions, hunter_headings = OTHER # now I can always refer to these variables

    #plugging in the Hunter to target the next anticipated area for the target

    if distance_between(hunter_position, xy_estimate) > max_distance: #if I can't get to the position in time
        # I want to go to a known point and keep going there.
        heading_to_target = get_heading(hunter_position, OTHER['measurements'][0]) #grab the first measurement
        heading_difference = heading_to_target - hunter_heading
        turning = heading_difference
        distance = max_distance # full speed ahead!
        print "I'm moving to the point"
        if distance_between(hunter_position, OTHER['measurements'][0]) <= max_distance/2:
            distance = 0 #stay put
            heading_to_target = get_heading(hunter_position, OTHER['measurements'][1]) #point at the next one
            heading_difference = heading_to_target - hunter_heading
            turning = heading_difference
            print "I'm staying at the point in waiting"
    else:
        heading_to_target = get_heading(hunter_position, xy_estimate)
        heading_difference = heading_to_target - hunter_heading
        turning = heading_difference # turn towards the target
        distance_to_point = distance_between(hunter_position, xy_estimate)
        distance = distance_to_point #I don't want to travel full speed LOL
        print "ATTACK!"

    return turning, distance, OTHER

def distance_between(point1, point2):
    """Computes distance between point1 and point2. Points are (x, y) pairs."""
    x1, y1 = point1
    x2, y2 = point2
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def demo_grading_visual(hunter_bot, target_bot, next_move_fcn, OTHER = None):
    """Returns True if your next_move_fcn successfully guides the hunter_bot
    to the target_bot. This function is here to help you understand how we
    will grade your submission."""
    max_distance = 0.98 * target_bot.distance # 1.94 is an example. It will change.
    separation_tolerance = 0.02 * target_bot.distance # hunter must be within 0.02 step size to catch target
    caught = False
    ctr = 0
    #For Visualization
    import turtle
    window = turtle.Screen()
    window.bgcolor('white')
    chaser_robot = turtle.Turtle()
    chaser_robot.shape('arrow')
    chaser_robot.color('blue')
    chaser_robot.resizemode('user')
    chaser_robot.shapesize(0.3, 0.3, 0.3)
    broken_robot = turtle.Turtle()
    broken_robot.shape('turtle')
    broken_robot.color('green')
    broken_robot.resizemode('user')
    broken_robot.shapesize(0.3, 0.3, 0.3)
    size_multiplier = 15.0 #change Size of animation
    chaser_robot.hideturtle()
    chaser_robot.penup()
    chaser_robot.goto(hunter_bot.x*size_multiplier, hunter_bot.y*size_multiplier-100)
    chaser_robot.showturtle()
    broken_robot.hideturtle()
    broken_robot.penup()
    broken_robot.goto(target_bot.x*size_multiplier, target_bot.y*size_multiplier-100)
    broken_robot.showturtle()
    measuredbroken_robot = turtle.Turtle()
    measuredbroken_robot.shape('circle')
    measuredbroken_robot.color('red')
    measuredbroken_robot.penup()
    measuredbroken_robot.resizemode('user')
    measuredbroken_robot.shapesize(0.1, 0.1, 0.1)
    broken_robot.pendown()
    chaser_robot.pendown()
    #End of Visualization
    # We will use your next_move_fcn until we catch the target or time expires.
    while not caught and ctr < 1000:
        # Check to see if the hunter has caught the target.
        hunter_position = (hunter_bot.x, hunter_bot.y)
        target_position = (target_bot.x, target_bot.y)
        separation = distance_between(hunter_position, target_position)
        if separation < separation_tolerance:
            print "You got it right! It took you ", ctr, " steps to catch the target."
            caught = True

        # The target broadcasts its noisy measurement
        target_measurement = target_bot.sense()

        # This is where YOUR function will be called.
        turning, distance, OTHER = next_move_fcn(hunter_position, hunter_bot.heading, target_measurement, max_distance, OTHER)

        # Don't try to move faster than allowed!
        if distance > max_distance:
            distance = max_distance

        # We move the hunter according to your instructions
        hunter_bot.move(turning, distance)

        # The target continues its (nearly) circular motion.
        target_bot.move_in_circle()
        #Visualize it
        measuredbroken_robot.setheading(target_bot.heading*180/pi)
        measuredbroken_robot.goto(target_measurement[0]*size_multiplier, target_measurement[1]*size_multiplier-100)
        measuredbroken_robot.stamp()
        broken_robot.setheading(target_bot.heading*180/pi)
        broken_robot.goto(target_bot.x*size_multiplier, target_bot.y*size_multiplier-100)
        chaser_robot.setheading(hunter_bot.heading*180/pi)
        chaser_robot.goto(hunter_bot.x*size_multiplier, hunter_bot.y*size_multiplier-100)
        #End of visualization
        ctr += 1
        if ctr >= 1000:
            print "It took too many steps to catch the target."
    return caught


def demo_grading(hunter_bot, target_bot, next_move_fcn, OTHER = None):
    """Returns True if your next_move_fcn successfully guides the hunter_bot
    to the target_bot. This function is here to help you understand how we
    will grade your submission."""
    max_distance = 0.98 * target_bot.distance # 0.98 is an example. It will change.
    separation_tolerance = 0.02 * target_bot.distance # hunter must be within 0.02 step size to catch target
    caught = False
    ctr = 0

    # We will use your next_move_fcn until we catch the target or time expires.
    while not caught and ctr < 1000:

        # Check to see if the hunter has caught the target.
        hunter_position = (hunter_bot.x, hunter_bot.y)
        target_position = (target_bot.x, target_bot.y)
        separation = distance_between(hunter_position, target_position)
        if separation < separation_tolerance:
            print "You got it right! It took you ", ctr, " steps to catch the target."
            caught = True

        # The target broadcasts its noisy measurement
        target_measurement = target_bot.sense()

        # This is where YOUR function will be called.
        turning, distance, OTHER = next_move_fcn(hunter_position, hunter_bot.heading, target_measurement, max_distance, OTHER)

        # Don't try to move faster than allowed!
        if distance > max_distance:
            distance = max_distance

        # We move the hunter according to your instructions
        hunter_bot.move(turning, distance)

        # The target continues its (nearly) circular motion.
        target_bot.move_in_circle()

        ctr += 1
        if ctr >= 1000:
            print "It took too many steps to catch the target."
    return caught



def angle_trunc(a):
    """This maps all angles to a domain of [-pi, pi]"""
    while a < 0.0:
        a += pi * 2
    return ((a + pi) % (pi * 2)) - pi

def get_heading(hunter_position, target_position):
    """Returns the angle, in radians, between the target and hunter positions"""
    hunter_x, hunter_y = hunter_position
    target_x, target_y = target_position
    heading = atan2(target_y - hunter_y, target_x - hunter_x)
    heading = angle_trunc(heading)
    return heading

def naive_next_move(hunter_position, hunter_heading, target_measurement, max_distance, OTHER):
    """This strategy always tries to steer the hunter directly towards where the target last
    said it was and then moves forwards at full speed. This strategy also keeps track of all
    the target measurements, hunter positions, and hunter headings over time, but it doesn't
    do anything with that information."""
    if not OTHER: # first time calling this function, set up my OTHER variables.
        measurements = [target_measurement]
        hunter_positions = [hunter_position]
        hunter_headings = [hunter_heading]
        OTHER = (measurements, hunter_positions, hunter_headings) # now I can keep track of history
    else: # not the first time, update my history
        OTHER[0].append(target_measurement)
        OTHER[1].append(hunter_position)
        OTHER[2].append(hunter_heading)
        measurements, hunter_positions, hunter_headings = OTHER # now I can always refer to these variables

    heading_to_target = get_heading(hunter_position, target_measurement)
    heading_difference = heading_to_target - hunter_heading
    turning =  heading_difference # turn towards the target
    distance = max_distance # full speed ahead!
    return turning, distance, OTHER

target = robot(0.0, 10.0, 0.0, 2*pi / 30, 1.5)
measurement_noise = .05*target.distance
target.set_noise(0.0, 0.0, measurement_noise)

hunter = robot(-10.0, -10.0, 0.0)

print demo_grading_visual(hunter, target, next_move)





