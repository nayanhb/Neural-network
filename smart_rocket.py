import math

import pygame as py

import random

class DNA:
    def __init__(self,lent):
        self.maxforce = 1
        self.gene = list()
        
        for _ in range(lent):
            v = py.Vector2(1, 0).rotate(random.uniform(0, 360))
            self.gene.append(v * random.uniform(0, self.maxforce))

    def crossover(self,parent):
        child = DNA(len(self.gene))
		
        midpoint = random.randint(0,len(self.gene) - 1)
		
        for i in range(len(self.gene)):
            if i < midpoint:
                child.gene[i] = self.gene[i].copy()
            else:
                child.gene[i] = parent.dna.gene[i].copy()
		
        return child
        
    def mutate(self, rate):
        for i in range(len(self.gene)):
            if random.random() < rate:
                self.gene[i] = py.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * random.uniform(0, self.maxforce)
        

class Rocket:
    def __init__(self,x:int,y:int,dna:DNA):
        self.pos = py.Vector2(x,y)
        self.vel = py.Vector2(0,0)
        self.acc = py.Vector2(0,0)
        
        self.dna = dna
        self.fitness = 0
        
        self.geneCount = 0
        
        self.recordDistance = float("inf")
        self.hitObstacle = False
        self.hitTarget = False
        
        self.finishCounter = 1 #for division error 
        
    def run(self,obstacles,target):
        if not self.hitObstacle and not self.hitTarget:
            self.applyForce(self.dna.gene[self.geneCount])
        
            self.geneCount += 1
        
            self.update()
            self.checkObstacle(obstacles)
            self.checkTarget(target)
        
    def calculateFitness(self):
        self.fitness = math.pow(self.recordDistance*self.finishCounter,-4 )  # ty: ignore[invalid-argument-type]
        
        if self.hitObstacle: self.fitness *= 0.1
        
        if self.hitTarget: self.fitness *= 20
        
    def update(self):
        self.vel += self.acc
        self.pos += self.vel
        
        self.acc.update(0,0)
        
    def applyForce(self, force):
        self.acc += force
    
    def checkObstacle(self, obstacles):
        for obstacle in obstacles:
            if obstacle.contains(self.pos):
                self.hitObstacle = True
    
    def checkTarget(self,target):
        dx = self.pos.x - target.pos.x
        dy = self.pos.y - target.pos.y
        distance = math.sqrt((dx**2)+(dy**2))
        if distance < self.recordDistance:
            self.recordDistance = distance
        
        if target.contains(self.pos):
            self.hitTarget = True
        
        if not self.hitTarget:
            self.finishCounter += 1
    
    def draw(self, screen, col):
        angle = math.degrees(math.atan2(self.vel.y, self.vel.x))  # ty: ignore[invalid-argument-type]
        pts = [p.rotate(angle) + self.pos for p in SHAPE]
        py.draw.polygon(screen, col, pts)

class Obstacle:
    def __init__(self,x,y,w,h):
        self.pos = py.Vector2(x,y)
        self.w,self .h = w,h
   
    def contains(self,spot):
       return (spot.x > self.pos.x and
               spot.x < self.pos.x + self.w and
               spot.y > self.pos.y and
               spot.y < self.pos.y + self.h)
               
    def draw(self,screen,color=(100,100,100)):
       py.draw.rect(screen,color,(self.pos.x,self.pos.y,self.w,self.h))

class Population:
    def __init__(self,x,y,mutation:float,length):
        self.x = x
        self.y = y
        self.mutationRate = mutation
        
        self.population = list()
        
        self.generation = 0
        for _ in range(length):
            self.population.append(Rocket(self.x,self.y,DNA(LIFESPAN)))
    
    def fitness(self):
        for i in self.population:
            i.calculateFitness()
    
    def selection(self):
        totalFitness = 0
        for i in self.population:
            totalFitness += i.fitness
            
        for i in self.population:
            i.fitness /= totalFitness
    
    def reproduction(self):
        newPop = list()
        for _ in range(len(self.population)):
            parent1 = self.weightedSelection()
            parent2 = self.weightedSelection()
            
            child = parent1.dna.crossover(parent2)
            child.mutate(self.mutationRate)
            
            newPop.append(Rocket(self.x,self.y,child))
    
        self.population = newPop.copy()
        self.generation += 1
    
    def live(self, obstacles, target):
        for i in self.population:
            i.run(obstacles,target)
    
    def weightedSelection(self):
        index = 0
        start = random.random()
	
        while start > 0 and index < len(self.population):
            start -= self.population[index].fitness
            index += 1
		
        index -= 1
        return self.population[index]
    
    def draw(self,screen,col):
        for i in self.population:
            i.draw(screen,col)
            

py.init()
font = py.font.Font(None, 48)

clock = py.time.Clock()
screen = py.display.set_mode((0, 0), py.FULLSCREEN)
w, h = screen.get_size()
center =  w//2, h//2

SHAPE = [py.Vector2(10, 0), py.Vector2(-10, -6), py.Vector2(-10, 6)]
LIFESPAN = 200
TARGET = Obstacle(w//2, h//4,100,100)
LIFECOUNTER = 0
OBJECT = [Obstacle(w//2 - 100, h//2 -30, 200, 60), Obstacle(w //2 - 100 , h - 300, 200, 100)]


def setup(x,y):
    return (Population(x,y,0.01,500))  # ty: ignore[unresolved-reference, unused-ignore-comment]
        
def run(lifecounter ,population):
    if lifecounter < LIFESPAN:
        population.live(OBJECT,TARGET)
        lifecounter += 1
    else:
        lifecounter = 0
        population.fitness()
        population.selection()
        population.reproduction()
    return lifecounter

pop = setup(w//2,h - 50)

running = True
while running:
    clock.tick(60)
    
    for event in py.event.get():
        if event.type == py.QUIT:
            running = False
        elif event.type == py.FINGERDOWN:
            tx, ty = event.x * w, event.y * h  # touch position in pixels
            TARGET = Obstacle(tx,ty,100,100)
    screen.fill((10, 15, 5))
    
    LIFECOUNTER = run(LIFECOUNTER, pop)
    
    TARGET.draw(screen,(200,0,0))
    for obj in OBJECT:
        obj.draw(screen)
    pop.draw(screen,(0,255,0))
    
    gen_text = font.render(f"Generation: {pop.generation}", True, (255, 255, 255))
    life_text = font.render(f"Life: {LIFECOUNTER}/{LIFESPAN}", True, (255, 255, 255))
    screen.blit(gen_text, (20, 20))
    screen.blit(life_text, (20, 70))
    
    py.display.flip()
    
py.quit()