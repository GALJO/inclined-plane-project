# InclinedPlaneProject

### 0. Introduction

InclinedPlaneProject is program that simulates physics scenario of mass point moving on inclined plane.
You can provide plane tilt, point mass, point start velocity and friction coefficient.
It runs simulation based on *Pymunk* physics engine,
calculates model based on basic Newton's dynamics and returns results from physics engine,
model results and measurement errors.

### 1. Scenario

<hr/>
In this section, you can learn about scenario simulated in program. 
It does not contain detailed physics description and scaaarrry formulas :), only necessary descriptions and schemas.
<hr/>

(scheme 1.)

On scheme 1. you can see start snapshot of scenario. Block (representing point mass) starts in
wall-plane corner with velocity given by user.

(scheme 2.)

On schema 2., you can see snapshot of scenario taken some time after start. Due to friction
block stopped in some point on the plane. Now, the scenario can go two ways. Normally, it will proceed
to 3a. However, for some input data, it proceeds to 3b.

On schema 3a., you can see snapshot of scenario taken when block is back by the wall.
Block is about to collide (perfectly elastic collision) with the wall.
After collision, scenario is back in 1. point, but with smaller velocity due to friction.
Process from 1. to 3b. point is called *Full Cycle*, and it repeats until block (almost) stops.

(schema 3b.)

On scheme 3b. you can see snapshot of scenario after point 2. Friction is too big to block to
slide down the plane. It stops in the 2. point, creating so called *Not Full Cycle*. Scenario/simulation ends here.

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

(scheme 4.)

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

Basic transformations of $(2)$ using *Newton's Second Law of Motion*<sup>6</sup> and trigonometry
results in the following formulas:

<div style="text-align: center;">

 $x_{(k+1)} = \frac{v_{(k+1)0}^2}{2{g}(\sin{\theta}+\mu\cos{\theta})}$ &ensp;&ensp; $(3)$

$t_{(k+1)1} = \frac{v_{(k+1)0}}{g(\sin{\theta}+\mu\cos{\theta})}$ &ensp;&ensp; $(4)$

$t_{(k+1)2} = \frac{v_{(k+1)1}}{g(\sin{\theta}-\mu\cos{\theta})}$ &ensp;&ensp; $(5)$

$t_{k+1} = t_{(k+1)1} + t_{(k+1)2}$ &ensp;&ensp; $(6)$
</div>

With use of derived formulas $(1)$ - $(6)$ we can obtain full model data for $(k+1)$-th cycle
knowing only constants and $(k)$-th end velocity.
<hr>

TO POWINNO IŚĆ DO KOLEJNEJ SEKCJI
- Program uses presented above recurrence formulas to prepare theoretical model.
The program treats start velocity given by user as fictional (-1)-th cycle end velocity.
Program stops counting cycles when end velocity is very small, but not equal to zero, so
it is not completely accurate.
- Program predicts simulation behavior on theoretical model. If theoretical model had n-

#### Footnotes

[^1]:[Elastic and Inelastic Collisions](http://hyperphysics.phy-astr.gsu.edu/hbase/elacol.html) (Access: 11.12.2025)\
[^2]:[Kinetic Energy](http://hyperphysics.phy-astr.gsu.edu/hbase/ke.html) (Access: 11.12.2025)\
[^3]:[Conservation Laws](http://hyperphysics.phy-astr.gsu.edu/hbase/conser.html) (Access: 11.12.2025)\
[^4]:[Work Done by a Force](https://www.monash.edu/student-academic-success/physics/relationships-between-force,-energy-and-mass/work-done-by-a-force) (Access: 11.12.2025)\
[^5]:[Newton’s Laws of Motion](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/newtons-laws-of-motion/#newtons-first-law-inertia) (Access: 11.12.2025)
