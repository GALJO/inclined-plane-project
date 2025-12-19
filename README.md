# InclinedPlaneProject

### 0. The introduction.

The InclinedPlane is a program that simulates the physics scenario of a mass point moving on an inclined plane. It
calculates a model based on physic's formulas, runs a simulation based on the *Pymunk* physics engine and returns
comparative data.

#### Contents:

1. [The scenario.](#1-the-scenario)
2. a. [Input.](#2a-input)  
   b. [Output.](#2b-output)
3. [The theoretical model.](#3-the-theoretical-model)
4. [How to set up dev's environment.](#5-how-to-set-up-devs-environment)
5. [License.](#6-license)

### 1. The scenario.

<hr>  
In this section, you can learn about the scenario of the program. It does not contain a detailed physics description and scaaarrry formulas :), only necessary descriptions and schemas.  
<hr>  

The scenario is a set of cycles. A **cycle** is a repeating set of events in the scenario. One cycle has 3 stages:

![scheme 1.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme1.jpg)  
(scheme 1. - the start of a cycle)

- 1st stage - The block (representing the mass point) starts in the corner with the velocity opposite to the last
  cycle's end velocity.

![scheme 2.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme2.jpg)  
(scheme 2. - the middle of a cycle)

- 2nd stage - Due to the friction the block has stopped. Now, a cycle can go two ways. In most cases, the block slides
  back and proceeds to the 3rd stage. However, for some input data, it proceeds to the 2nd stage termination.

![scheme 3.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme3.jpg)  
(scheme 3. - the end of a cycle)

- 3rd stage - The block is about to collide with the wall. After the collision, the scenario is back in the 1st stage of
  the next cycle. A process from the 1st to the 3rd stage is called a **full cycle**, and it repeats until the block (
  almost) stops. The scenario is defined as a set of full cycles.
- 2nd stage termination - The friction is too big to the block to slide down the plane. The block stops in the 2nd
  stage, creating so called a **not full cycle**. The scenario ends here - it is defined as a one element set of *not
  full cycles*.

### 2a. Input.

<hr>  
In this section you will learn what data the user must provide.
<hr>  

- **Tilt ($\theta$) --** (default range: $0 < \theta < \frac{\pi}{2}$ unit: $rad$) -- The tilt angle of the surface,
- **Mass ($m$) --** (default range: $0 < m < \infty$ unit: $kg$) -- The mass of the point,
- **Start speed ($v$) --** (default range: $0 < v < \infty$ unit: $\frac{m}{s}$) -- The 1st cycle's start velocity value (
  velocity is parallel to the surface),
- **Friction ($\mu$) --** (default range: $0 < \mu < \infty$) -- The Coulomb's friction coefficient between the point and
  the surface.

### 2b. Output.

<hr>  
In this section you will learn what data program returns to the user.  
<hr>  

~~For now~~ There is only one output form - the .csv file. Each **row** contains data for the one cycle.  
One row contains ~~too much~~ just enough data about the simulation outcome.

There are three main sections in the CSV table - each of them are labeled by a header fix:

1. `*_measured` -- Simulation's results (measured during simulation).
2. `*_model` -- Model results (calculated using formulas).
3. `*_[abs/rel]_error_` -- Measurement errors (how much simulation's results are apart from physics formulas).  
   While the `abs` fix means an absolute error, the `rel` fix means a relative error.

In each section the `*` symbol means 6 values:

- `duration1` -- The duration between 1st and 2nd stage of the cycle.
- `duration2` -- The duration between 2nd and 3rd stage of the cycle.
- `duration` -- The duration of full cycle.
- `start_velocity_[x/y/value]` **(V)** -- The velocity in 1st stage of the cycle.
- `end_velocity_[x/y/value]` **(V)** -- The velocity in 3rd stage of the cycle.
- `reach_[x/y/value]` **(V)** -- The distance traveled by the point between 1st and 2nd stage of the cycle.

**(V)** -- It is the vector value, so it has 3 fields - XY coordinates and the vector's value.

Additional values:
`cycle_number` - number of the cycle starting from 1.  
`is_full` - True if the cycle is full, else False.

All these headers sum up to outstanding **50** values for each cycle!

### 3. The theoretical model.

<hr>

Fair warning, this section is intended for ~~physics geeks~~ anyone, who wants to know more about  
physics model of the scenario. I recommend to start with reading other sections.
<hr>  

Let us introduce the notation for variables and constants.

A **cycle** is defined in **The scenario** section.

#### Variables.

- $\vec{v_{k0}}$ - The start velocity of the $k$-th cycle.
- $\vec{v_{k1}}$ - The end velocity of the $k$-th cycle (hereinafter referred to as the *$k$-th end velocity*).
- $\vec{x_{k}}$ - The displacement vector of the point between the 1st and the 2nd step of the $k$-th cycle.
- $t_{k1}$ - The time elapsed between the 1st and the 2nd step of the $k$-th cycle.
- $t_{k2}$ - The time elapsed between the 2nd and the 3rd step of $k$-th cycle.
- $t_{k}$ - The full duration of the $k$-th cycle.

#### Constants.

- $\theta$ - The tilt angle of the surface.
- $\vec{v_{01}}$ - The scenario's start velocity.
- $\vec{g} =$ (by default) $[0, -9.81] \frac{m}{s^2}$ - The gravitational acceleration.
- $\mu$ - The Coulomb's friction coefficient between the mass point and the surface.

For any vector $\vec{k} \in \mathbb{R}^2$ we adopt the following notation:

<div style="text-align: center;">  

$\|\vec{k}\| = k$

$\vec{k} = [k_x, k_y]$

</div>  
<hr>  

![scheme 4.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme1.jpg)  
(scheme 4. - the start of the $k$-th cycle)

The static, tilted surface is hereinafter referred to as the *plane*.  
The static, perfectly elastic surface, normal to the plane is hereinafter referred to as the *wall*.  
The dynamic mass point (on scheme 4. presented as the green block) is hereinafter referred to as the *point*.

$\vec{T}$ - The friction force between the point and the plane.  
$\vec{Q}$ - The point's gravity force.  
$\vec{R}$ - The plane's reaction force to the normal of the point's gravity force.

Between the end of any $k$-th cycle and the start of the $(k+1)$-th cycle one and only event is the perfectly elastic
collision between the point and the wall. According to collision's mechanics:  *A perfectly elastic collision is defined
as one in which there is no loss of kinetic energy in the collision.*[^1]. As the wall is the static object ($E=0$), the
kinetic energy of the point is equal at the end of the $k$-th cycle and start of the $(k+1)$-th cycle. Therefore, there
is a recurrence relation between adjacent _cycles_ that can be expressed as[^2]:

<div style="text-align: center;">  

$v_{(k+1)0} = v_{k1}$ &ensp;&ensp; $(1)$

</div>  

According to the law of the conservation of the energy: *Total energy of an isolated system remains constant.*[^3]
However, our model is not isolated due to the non-conservative force $\vec{T}$[^4]. After including the friction's
force's work $W_T$[^5] in the conservation of the energy formula we obtain:

<div style="text-align: center;">  

$v_{(k+1)1} = v_{(k+1)0}\sqrt{\frac{\sin{\theta}-\mu\cos{\theta}}{\sin{\theta}+\mu\cos{\theta}}}$ &ensp;&ensp; $(2)$

</div>  

Transformations of $(2)$ using kinematic's formulas and the *Newton's Second Law of Motion*[^6]  
results in the following formulas:

<div style="text-align: center;">  

$x_{(k+1)} = \frac{v_{(k+1)0}^2}{2{g}(\sin{\theta}+\mu\cos{\theta})}$ &ensp;&ensp; $(3)$

$t_{(k+1)1} = \frac{v_{(k+1)0}}{g(\sin{\theta}+\mu\cos{\theta})}$ &ensp;&ensp; $(4)$

$t_{(k+1)2} = \frac{v_{(k+1)1}}{g(\sin{\theta}-\mu\cos{\theta})}$ &ensp;&ensp; $(5)$

$t_{k+1} = t_{(k+1)1} + t_{(k+1)2}$ &ensp;&ensp; $(6)$

</div>  

Using formulas $(1)$ - $(6)$ we obtain full model data for the $(k+1)$-th cycle  
knowing only constants and the $k$-th end velocity.

There is a corner case when the $\vec{T}$ value is bigger than the horizontal $\vec{Q}$ value.  
In this situation, in the 2nd stage the $\vec{T}$ transforms to the static friction $\vec{T_s}$ and the point stops
moving. This happens if and only if the following formula is true:

<div style="text-align: center;">  

$\frac{\mu\cos{\theta}}{sin{\theta}} \geq 1$ &ensp;&ensp; (7)

</div>  
<hr>

#### The theoretical model in practice.

- $(1)$ - $(6)$ recurrence formulas are being used to prepare the theoretical model of scenario,
- The $\vec{v_{01}}$ is provided by the user,
- Cycles are being counted until the $n$-th end velocity is (close to) zero,
- Before counting cycles, it is checked if the not full cycle occurred based on the $(7)$ formula,
- The simulation's results are being predicted based on the theoretical model.

### 4. The simulation's details.

<hr>  
In this section you can learn some technical facts and issues with the simulation in the program.  
<hr>  

The simulation run on the *[Pymunk](https://www.pymunk.org)* physics engine and the *[Pygame](https://www.pygame.org)*
graphical interface.  
In the simulation the mass point is replaced with the homogeneous block with infinite inertia, which  
is good approximation of the mass point in physics.

A main objective of the simulation is to visualize the scenario for user. Therefore, the simulation  
is scaled up, because it does not look good with real numbers. However, proportions are kept and  
the program *unscales* simulation's measurements and final results are not scaled.

If the user uses too big starting velocity, block may fall out of the simulation due to the limitations of the space.

### 5. How to set up dev's environment.

<hr>  
This section is for developers, who want to set up their own development environment.     
<hr>  

#### Prerequisites.

- Python 3.14,
- Cloned repository of InclinedPlaneProject.

#### The first setup.

This project is using the *[Pipenv](https://pipenv.pypa.io/en/latest/)* Python's module as a package manager,  
so a setup is nice and easy. Just follow these steps:

1. Install the *Pipenv* with the Python's pip module.

```
python -m pip install pipenv=2026.0.*
```

2. Set up a Pipenv shell in the repo folder.

```
cd [path to repo]
pipenv shell --python 3.14
```

3. While in the Pipenv shell install all packages.

```
pipenv update
```

4. Run `main.py`.

```
python src/main.py
```

Happy coding!

#### Back again

Let's say you completed your first setup, turned off the computer and went for some ***power nap***.  
How to get back to the environment? It's easy:

```  
cd [path to repo]  
pipenv shell  
python src/main.py  
```  

Voilà! Happy coding!

### 6. License

<hr>  
This section describes licensing of the software.  
<hr>

This software is licensed under the ***[Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0)*** license. For easy
explain what you can/cannot/must do look up [there](https://www.tldrlegal.com/license/apache-license-2-0-apache-2-0).

#### NOTICE

Copyright 2025 Jan Oleński

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. See the License for the specific language governing
permissions and limitations under the License.

[^1]: [Elastic and Inelastic Collisions](http://hyperphysics.phy-astr.gsu.edu/hbase/elacol.html) (Access: 11.12.2025)

[^2]: [Kinetic Energy](http://hyperphysics.phy-astr.gsu.edu/hbase/ke.html) (Access: 11.12.2025)

[^3]: [Conservation Laws](http://hyperphysics.phy-astr.gsu.edu/hbase/conser.html) (Access: 11.12.2025)

[^4]: [Coulomb Friction](https://www.sciencedirect.com/topics/engineering/coulomb-friction) (Access: 11.12.2025)

[^5]: [Work Done by a Force](https://www.monash.edu/student-academic-success/physics/relationships-between-force,-energy-and-mass/work-done-by-a-force) (
Access: 11.12.2025)

[^6]: [Newton’s Laws of Motion](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/newtons-laws-of-motion/#newtons-first-law-inertia) (
Access: 11.12.2025)