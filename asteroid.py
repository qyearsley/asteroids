import pygame

from circleshape import CircleShape

class Asteroid(CircleShape):
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius)

    def update(self, dt):
        self.position += self.velocity * dt
