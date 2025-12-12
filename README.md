# InclinedPlaneProject

### 0. Introduction

InclinedPlaneProject is a program that simulates physics scenario of mass point moving on inclined plane.
You can provide plane tilt, point mass, point start velocity and friction coefficient.
It runs simulation based on *Pymunk* physics engine,
calculates model based on basic Newton's dynamics and returns results from physics engine,
model results and measurement errors.

### 1. Scenario

<hr/>
In this section, you can learn about scenario of the program. 
It does not contain detailed physics description and scaaarrry formulas :), only necessary descriptions and schemas.
<hr/>

Scenario is defined as set of the *Cycles* - repeating set of events in scenario. 
One *Cycle* contains 3 stages:

![scheme 1.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme1.jpg)
(scheme 1. - start of the cycle)

- 1-st stage - Block (representing point mass) starts in
the corner with velocity opposite to the last cycle end velocity (if it is first cycle it is user start velocity).

![scheme 2.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme2.jpg)
(scheme 2. - middle of the cycle)

- 2-nd stage - Due to friction block has stopped. Now, the cycle can go two ways. 
In most cases, block slides back and proceeds to 3-rd stage. 
However, for some input data, it proceeds to 2-nd stage termination.

![scheme 3.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme3.jpg)
(scheme 3. - type A end of the cycle)

- 3-rd stage type A - Block is about to collide with the wall.
After collision, scenario is back in 1-st stage of the next cycle.
Process from 1-st to 3-rd type A stage is called *Full Cycle*, and it repeats until block (almost) stops.
Scenario is defined as set of *Full Cycles*.

- 2-nd stage termination - Friction is too big to block to slide down the plane. 
It stops in the 2-nd stage, creating so called *Not Full Cycle*. Scenario ends here - it is defined
as one *Not Full Cycle*.

### 2a. Input

<hr/>
In this section you will learn what data program reads from you (constants of simulation):
<hr/>

- Plane tilt (radians) - Angle between horizon and plane.
  Program accepts values between $0$ and $\frac{\pi}{2}$ radians (0 to 90 degrees). It does not accept
  values (almost) equal $0$ and $\frac{\pi}{2}$ radians.

- Point mass (kilograms) - Mass of the point mass. It must be bigger than $0$.

-

### 2b. Output

<hr/>
In this section you will learn what data program returns to you and in what form.
<hr/>

~~For now~~ There is only one output form - .csv file with table. Each **row** contains data for one scenario cycle.
One row contains ~~too much~~ just enough data about simulation outcome.

#### Columns

- **Lorem**

### 3. Physics theoretical model

<hr>

Fair warning, this section is intended for ~~physics geeks~~ anyone, who wants to know more about
physics model of scenario. I recommend to start with reading other sections.
<hr>

Let us introduce notation for further use of variables and constants.

#### Variables

- $v_{k0}$ - Start speed of $k$-th cycle.
- $v_{k1}$ - End speed of $k$-th (hereinafter referred to as *$k$-th end speed*).
- $x_{k}$ - Value of vector between 1. and 2. points of $k$-th cycle point positions.
- $t_{k1}$ - Time elapsed between 1. and 2. point of $k$-th cycle.
- $t_{k2}$  - Time elapsed between 2. and 3. point of $k$-th cycle.
- $t_{k}$ - Full duration of $k$-th cycle.

#### Constants

- $\theta$ - Angle between horizon and the tilted surface.
- $v_{01}$ - Simulation start speed.
- $\vec{g} = [0, -9.81] \frac{m}{s^2}$ - Gravitational acceleration.
- $\mu$ - Friction coefficient.

For any vector $\vec{k} \in \mathbb{R}^2$ we adopt the following notation:
<div style="text-align: center;">

$\|\vec{k}\| = k$

$\vec{k} = [k_x, k_y]$
</div>
<hr>

![scheme 4.](https://raw.githubusercontent.com/GALJO/inclined-plane-project/refs/heads/master/doc/scheme1.jpg)
(scheme 4. - beginning of the cycle)

Static, tilted surface is hereinafter referred to as *the plane*

Static, perfectly elastic surface, perpendicular to the plane is hereinafter referred to as *the wall*.

Dynamic mass point (on schema presented as a block) is *h*ereinafter referred to as *the point*.

Between the end of any $k$-th cycle and the start of $(k+1)$-th cycle
one and only event is perfectly elastic collision between the point and the wall.
According to collision's mechanics:
*A perfectly elastic collision is defined as one in which there is no loss of kinetic energy in the collision.*[^1].
As the wall is static object ($E=0$), kinetic energy of the point is equal at the end of $k$-th cycle
and start of $(k+1)$-th cycle.

Therefore, there is a recurrence relation between adjacent cycles that can be expressed as[^2]:

<div style="text-align: center;">

$v_{(k+1)0} = v_{k1}$ &ensp;&ensp; $(1)$
</div>

According to the law of conservation of energy:
*Total energy of an isolated system remains constant.*[^3],
However, our model is not isolated due to the friction[^4], therefore
we need to consider it. After including work of the friction[^5] in the
conservation of energy formula and performing basic algebra and trygonometry, we get:

<div style="text-align: center;">

$v_{(k+1)1} = v_{(k+1)0}\sqrt{\frac{2\tan{\theta}-\mu}{2(\mu+\tan{\theta})}}$ &ensp;&ensp; $(2)$
</div>

Basic transformations of $(2)$ using *Newton's Second Law of Motion*[^6] and trigonometry
results in the following formulas:

<div style="text-align: center;">

$x_{(k+1)} = \frac{v_{(k+1)0}^2}{2{g}(\sin{\theta}+\mu\cos{\theta})}$ &ensp;&ensp; $(3)$

$t_{(k+1)1} = \frac{v_{(k+1)0}}{g(\sin{\theta}+\mu\cos{\theta})}$ &ensp;&ensp; $(4)$

$t_{(k+1)2} = \frac{v_{(k+1)1}}{g(\sin{\theta}-\mu\cos{\theta})}$ &ensp;&ensp; $(5)$

$t_{k+1} = t_{(k+1)1} + t_{(k+1)2}$ &ensp;&ensp; $(6)$
</div>

With use of derived formulas $(1)$ - $(6)$ we can obtain full model data for $(k+1)$-th cycle
knowing only constants and $k$-th end velocity.

There is a corner case when kinetic friction force is
bigger than projection of the gravitation vector onto the horizont. 
In 2-nd cycle stage kinetic friction changes to static friction and the point stops moving.
This corner case happens if and only if the following formula is true:
<div style="text-align: center;">

$\frac{\mu\cos{\theta}}{sin{\theta}} \geq 1$ &ensp;&ensp; (7)
</div>
<hr>

#### Theoretical model in practice
- Program uses $(1)$ - $(6)$ recurrence formulas to prepare theoretical model.
The program treats start velocity given by user as fictional $0$-th end velocity.
Program stops counting cycles when $n$-th end velocity is close to zero.
- Program checks *Not Full Cycle* occurrence based on (7) formula.
- Program predicts simulation behavior based on theoretical model. 
If theoretical model had ${n}$ cycles then simulation also waits for ${n}$ cycles before end.
If theoretical model had *Not Full Cycle* then simulation is also prepared for this case.
- Simulation errors are prepared based on theoretical model and using basic error formulas.
<hr>

### 4. Simulation details

To simulate scenario program uses *[Pymunk](https://www.pymunk.org)* 
physics engine and *[Pygame](https://www.pygame.org)* graphical interface.
In simulation mass point is replaced with homogeneous block with infinite inertia, which
is good approximation to the mass point in physics.

Main objective of the simulation is to visualize the scenario for user. Therefore, simulation
is scaled up, because it does not look good with real numbers. However, proportions are kept and  
program "unscales" simulation measurements and final results are in 1:1 scale.

If user uses too big starting velocity, block may fall out of the simulation due to limitations
of space.

You can observe that with every simulation cycle, it gets less precise.

<hr>

#### 5. Footnotes

[^1]:[Elastic and Inelastic Collisions](http://hyperphysics.phy-astr.gsu.edu/hbase/elacol.html) (Access: 11.12.2025)\
[^2]:[Kinetic Energy](http://hyperphysics.phy-astr.gsu.edu/hbase/ke.html) (Access: 11.12.2025)\
[^3]:[Conservation Laws](http://hyperphysics.phy-astr.gsu.edu/hbase/conser.html) (Access: 11.12.2025)\
[^4]:[Work Done by a Force](https://www.monash.edu/student-academic-success/physics/relationships-between-force,-energy-and-mass/work-done-by-a-force) (Access: 11.12.2025)\
[^5]:[Coulomb Friction](https://www.sciencedirect.com/topics/engineering/coulomb-friction) (Access: 11.12.2025)\
[^6]:[Newton’s Laws of Motion](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/newtons-laws-of-motion/#newtons-first-law-inertia) (Access: 11.12.2025)
