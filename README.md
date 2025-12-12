# InclinedPlaneProject

### 0. Introduction

InclinedPlaneProject is a program that simulates the physics scenario of a mass point moving on an inclined plane.
You can provide a plane tilt, a point's mass, a point start velocity and a friction coefficient.
It runs simulation based on the *Pymunk* physics engine,
calculates the model based on basic kinematics and dynamics and returns results from the physics engine,
model results and measurement errors.

#### Contents
1. [Scenario](#1-scenario)
2. a. [Input](#2a-input)\
   b. [Output](#2b-output)
3. [Physics theoretical model](#3-physics-theoretical-model)
4. [Simulation details](#4-simulation-details)
5. [Setup development environment](#5-setup-development-environment)
6. [License](#6-license)

### 1. Scenario
<hr>
In this section, you can learn about the scenario of the program. 
It does not contain a detailed physics description and scaaarrry formulas :), only necessary descriptions and schemas.
<hr>

The scenario is defined as a set of *cycles*: A **cycle** is a repeating set of events in the scenario. 
One *cycle* is 3 stages:

![scheme 1.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme1.jpg)
(scheme 1. - start of a cycle)

- 1st stage - The block (representing the mass point) starts in
the corner with the velocity opposite to the last cycle's end velocity.

![scheme 2.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme2.jpg)
(scheme 2. - middle of a cycle)

- 2nd stage - Due to the friction the block has stopped. Now, a cycle can go two ways. 
In most cases, the block slides back and proceeds to the 3rd stage. 
However, for some input data, it proceeds to the 2nd stage termination.

![scheme 3.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme3.jpg)
(scheme 3. - end of a cycle)

- 3rd stage - The block is about to collide with the wall.
After the collision, the scenario is back in the 1st stage of the next cycle.
A process from the 1st to the 3rd stage is called a **full cycle**, and it repeats until the block (almost) stops.
The scenario is defined as a set of full cycles.

- 2nd stage termination - The friction is too big to the block to slide down the plane. 
The block stops in the 2nd stage, creating so called a **not full cycle**. The scenario ends here - it is defined
as a one element set of *not full cycles*.

### 2a. Input
<hr/>
In this section you will learn what data program reads from you (constants of simulation):
<hr/>

- **Lorem**

### 2b. Output

<hr/>
In this section you will learn what data program returns to you and in what form.
<hr/>

~~For now~~ There is only one output form - the .csv file with table. Each **row** contains data for the one cycle.
One row contains ~~too much~~ just enough data about the simulation outcome.

#### Columns

- **Lorem**

### 3. Physics theoretical model

<hr>

Fair warning, this section is intended for ~~physics geeks~~ anyone, who wants to know more about
the physics model of the scenario. I recommend to start with reading other sections.
<hr>

Let us introduce the notation for further use of the variables and the constants.

A **cycle** is defined in **Scenario** section.

#### Variables

- $\vec{v_{k0}}$ - Start velocity of the $k$-th cycle.
- $\vec{v_{k1}}$ - End velocity of the $k$-th cycle (hereinafter referred to as the *$k$-th end velocity*).
- $\vec{x_{k}}$ - Vector between the 1st and the 2nd step of the $k$-th cycle point positions (range).
- $t_{k1}$ - Time elapsed between the 1st and the 2nd step of the $k$-th cycle.
- $t_{k2}$  - Time elapsed between the 2nd and the 3rd step of $k$-th cycle.
- $t_{k}$ - Full duration of the $k$-th cycle.

#### Constants

- $\theta$ - The angle between horizontal and the tilted surface.
- $\vec{v_{01}}$ - Scenario's start velocity.
- $\vec{g} = [0, -9.81] \frac{m}{s^2}$ - Gravitational acceleration.
- $\mu$ - Friction coefficient between the mass point and the surface.

For any vector $\vec{k} \in \mathbb{R}^2$ we adopt the following notation:
<div style="text-align: center;">

$\|\vec{k}\| = k$

$\vec{k} = [k_x, k_y]$
</div>
<hr>

![scheme 4.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme1.jpg)
(scheme 4. - beginning of the cycle)

Static, tilted surface is hereinafter referred to as the *plane*.\
Static, perfectly elastic surface, normal to the *plane* (on scheme 4. at the end of the _plane_) 
is hereinafter referred to as the *wall*.\
Dynamic mass point (on scheme 4. presented as the green block) is *hereinafter referred to as the *point*.



$\vec{T}$ - Friction between the *point* and the *plane*.\
$\vec{Q}$ - The *point*'s gravity force.\
$\vec{R}$ - The *plane*'s reaction to the normal of the *point's gravity force.

Between the end of any $k$-th cycle and the start of $(k+1)$-th cycle
one and only event is perfectly elastic collision between the *point* and the *wall*.
According to collision's mechanics:
*A perfectly elastic collision is defined as one in which there is no loss of kinetic energy in the collision.*[^1].
As the *wall* is the static object ($E=0$), kinetic energy of the *point* is equal at the end of $k$-th _cycle_
and start of $(k+1)$-th _cycle_. Therefore, there is a recurrence relation between adjacent _cycles_ that can be expressed as[^2]:

<div style="text-align: center;">

$v_{(k+1)0} = v_{k1}$ &ensp;&ensp; $(1)$
</div>

According to the law of conservation of energy:
*Total energy of an isolated system remains constant.*[^3],
However, our model is not isolated due to the $\vec{T}$[^4], therefore
we need to consider it in our calculations. After including $W_T$ (work of friction)[^5] in the 
conservation of energy formula and performing basic algebra and trygonometry, we get:

<div style="text-align: center;">

$v_{(k+1)1} = v_{(k+1)0}\sqrt{\frac{2\tan{\theta}-\mu}{2(\mu+\tan{\theta})}}$ &ensp;&ensp; $(2)$
</div>

Basic transformations of $(2)$ using basic kinematic's formulas, *Newton's Second Law of Motion*[^6] 
and trigonometry results in the following formulas:

<div style="text-align: center;">

$x_{(k+1)} = \frac{v_{(k+1)0}^2}{2{g}(\sin{\theta}+\mu\cos{\theta})}$ &ensp;&ensp; $(3)$

$t_{(k+1)1} = \frac{v_{(k+1)0}}{g(\sin{\theta}+\mu\cos{\theta})}$ &ensp;&ensp; $(4)$

$t_{(k+1)2} = \frac{v_{(k+1)1}}{g(\sin{\theta}-\mu\cos{\theta})}$ &ensp;&ensp; $(5)$

$t_{k+1} = t_{(k+1)1} + t_{(k+1)2}$ &ensp;&ensp; $(6)$
</div>

With use of derived formulas $(1)$ - $(6)$ we can obtain full model data for $(k+1)$-th cycle
knowing only constants and $k$-th end velocity.

There is a corner case when $\vec{T}$ is bigger than horizontal $\vec{Q}$ value. 
In this situation, in 2-nd stage $\vec{T}$ changes to static friction ($\vec{T_s}$)
and the point stops moving.
This happens if and only if the following formula is true:
<div style="text-align: center;">

$\frac{\mu\cos{\theta}}{sin{\theta}} \geq 1$ &ensp;&ensp; (7)
</div>
<hr>

#### Theoretical model in practice
- Program uses $(1)$ - $(6)$ recurrence formulas to prepare theoretical model.
The program treats start velocity given by user as fictional $0$-th end velocity.
Program stops counting cycles when $n$-th end velocity is close to zero.
- Program checks *Not Full Cycle* occurrence based on $(7)$ formula.
- Program predicts simulation behavior based on theoretical model. 
If theoretical model has ${n}$ *cycles* then simulation waits for ${n}$ *cycles* before ending.
If theoretical model had *Not Full Cycle* then simulation is also prepared for this case.
- Simulation errors are prepared with data from theoretical model as a true values using basic error formulas.

### 4. Simulation details
<hr>
In this section you can learn some technical facts and issues with the simulation carried out by the program.
<hr>

Simulation is carried out by *[Pymunk](https://www.pymunk.org)* physics engine and *[Pygame](https://www.pygame.org)* graphical interface.
In simulation mass point is replaced with homogeneous block with infinite inertia, which
is good approximation to the mass point in physics.

Main objective of the simulation is to visualize the scenario for user. Therefore, simulation
is scaled up, because it does not look good with real numbers. However, proportions are kept and  
program "unscales" simulation measurements and final results are in 1:1 scale.

If user uses too big starting velocity, block may fall out of the simulation due to limitations
of space.

You can observe, that with every simulation cycle, results gets less precise.

### 5. Setup development environment
<hr>
This section is for developers, who want to work on that project, make some experiments or own modifications.   
<hr>

#### Prerequisites
- Python 3.12 with pip,
- Cloned repository of InclinedPlaneProject.

#### First setup
Project is using [Pipenv](https://pipenv.pypa.io/en/latest/) python module as package manager, 
so environment setup is nice and easy. Just follow these steps:
1. Install pipenv with python pip module.
```
pip install pipenv=2026.0.2
```
2. Setup pipenv shell in repo folder.
```
cd [path to repo]
pipenv shell --python 3.12
```
3. While in pipenv shell install all packages.
```
pipenv install
```
4. Run `main.py`.
```
python3 src/main.py
```
Happy coding!

#### Back again
Let's say you completed your first setup, turned off computer and went for some **power nap**.
How to get back to the environment? It's easy:
```
cd [path to repo]
pipenv shell
python3 src/main.py
```
and Voilà!

#### Important notice
You did something cool with my project and want to share it? 
Remember to follow Terms and Conditions in LICENSE file.

### 6. License
<hr>
This section describes licensing of the software.
<hr>
This software is licensed under [Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0) license.
The license is open-source with certain distribution rules. 
For easy explain what you can/cannot/must do 
look up [there](https://www.tldrlegal.com/license/apache-license-2-0-apache-2-0).
You can find full license text in LICENSE file alongside with the notice in NOTICE file.


[^1]:[Elastic and Inelastic Collisions](http://hyperphysics.phy-astr.gsu.edu/hbase/elacol.html) (Access: 11.12.2025)
[^2]:[Kinetic Energy](http://hyperphysics.phy-astr.gsu.edu/hbase/ke.html) (Access: 11.12.2025)
[^3]:[Conservation Laws](http://hyperphysics.phy-astr.gsu.edu/hbase/conser.html) (Access: 11.12.2025)
[^4]:[Coulomb Friction](https://www.sciencedirect.com/topics/engineering/coulomb-friction) (Access: 11.12.2025)
[^5]:[Work Done by a Force](https://www.monash.edu/student-academic-success/physics/relationships-between-force,-energy-and-mass/work-done-by-a-force) (Access: 11.12.2025)
[^6]:[Newton’s Laws of Motion](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/newtons-laws-of-motion/#newtons-first-law-inertia) (Access: 11.12.2025)
