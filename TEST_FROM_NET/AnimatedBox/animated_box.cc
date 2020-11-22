/*
 * Copyright (C) 2012 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
*/
#include <gazebo/gazebo.hh>
#include <ignition/math.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <stdio.h>

#include <unistd.h>
#include <ctime>
#include <math.h>

#define _USE_MATH_DEFINES


#define MIN_ANGLE   5 
#define MAX_ANGLE   60
#define MIN_SPEED   5
#define MAX_SPEED   20
#define MIN_HEIGHT  2
#define MAX_HEIGHT  10
#define GRAVITY     9.81

typedef struct Coords{
  double x, y, z;
} Coords;


Coords getNextCoords(float time, float speed, float height, float alpha, float beta){

  // Coords coords;
  // coords.x = cos(alpha) * speed * time;
  // coords.z = (-0.5 * GRAVITY * time * time) + (sin(alpha) * speed * time) + height;
  // coords.y = cos(beta) * speed * time;

  // printf("time: %f\tx: %f\ty: %f\tz: %f\talpha: %f\tbeta: %f\theight: %f\tspeed: %f\n", 
  //   time, coords.x, coords.y, coords.z, alpha, beta, height, speed);

  // return coords;

  printf("\n******************\ncos(%f): %g\tcos(%f): %g\tsin(%f): %g\n******************\n",
    alpha,
    cos(alpha),
    beta,
    cos(beta),
    alpha,
    sin(alpha)
  );
  return {
    cos(alpha) * speed * time,
    cos(beta) * speed * time,
    (-0.5 * GRAVITY * time * time) + (sin(alpha) * speed * time) + height
  };

}


void printCoords(Coords coords){

  printf("x: %f\ty: %f\tz: %f\n",
    coords.x, coords.y, coords.z
  );

}


namespace gazebo
{
  class AnimatedBox : public ModelPlugin
  {
    public: void Load(physics::ModelPtr _parent, sdf::ElementPtr /*_sdf*/)
    {
      // Store the pointer to the model
      this->model = _parent;

        // create the animation
        gazebo::common::PoseAnimationPtr anim(
              // name the animation "test",
              // make it last 10 seconds,
              // and set it on a repeat loop
              new gazebo::common::PoseAnimation("test", 10.0, true));

        gazebo::common::PoseKeyFrame *key;

        srand(time(NULL));
        float speed   = rand() % MAX_SPEED + MIN_SPEED;
        float height  = rand() % MAX_HEIGHT + MIN_HEIGHT; 
        float alpha   = rand() % MAX_ANGLE + MIN_ANGLE;
        float beta    = rand() % MAX_ANGLE + MIN_ANGLE;
        
        // float alpha = rand() % 45 + 15;
        // alpha = 90 ; beta = 0 ;
        printf("alpha : %g\tbeta: %g\theight: %g\tspeed: %g\n\n",
          alpha, beta, height, speed
        );
        alpha = alpha * M_PI / 180.; // From degrees to radians
        beta  = beta  * M_PI / 180.; // From degrees to radians


        float time, rotAngle;
        Coords ballCoords = {
          .0,
          .0,
          .0
        };

        
        printCoords(ballCoords);

        for (time = rotAngle = 0.0; ballCoords.z >= 0.0f ; time += .1f, ++rotAngle){

          ballCoords = getNextCoords(
            time,
            speed,
            height,
            alpha,
            beta 
          );

          printf("time: %f\t", time);
          printCoords(ballCoords);
      
          key = anim->CreateKeyFrame(time);
          key->Translation(ignition::math::Vector3d(
            ballCoords.x,
            ballCoords.y,
            ballCoords.z
          ));

          key->Rotation(ignition::math::Quaterniond(rotAngle, 0, 0));

          usleep(30000);

        }

        // set the animation
        _parent->SetAnimation(anim);
    }

    // Pointer to the model
    private: physics::ModelPtr model;

    // Pointer to the update event connection
    private: event::ConnectionPtr updateConnection;
  };

  // Register this plugin with the simulator
  GZ_REGISTER_MODEL_PLUGIN(AnimatedBox)
}

