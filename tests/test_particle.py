"""Tests for explosion particles: they burst, drift, and clean themselves up."""

import pytest

from constants import (
    PARTICLE_COUNT,
    PARTICLE_LIFETIME,
    PARTICLE_SPEED_MAX,
    PARTICLE_SPEED_MIN,
)
from particle import Particle, spawn_explosion


@pytest.fixture
def particles(container_for):
    return container_for(Particle)


def test_explosion_spawns_a_full_burst(particles):
    spawn_explosion(100, 100)
    assert len(particles) == PARTICLE_COUNT


def test_particles_drift_within_the_configured_speed_range(particles):
    spawn_explosion(100, 100)
    assert all(
        PARTICLE_SPEED_MIN <= particle.velocity.length() <= PARTICLE_SPEED_MAX
        for particle in particles
    )


def test_particle_survives_while_it_still_has_lifetime_left(particles):
    Particle(100, 100).update(PARTICLE_LIFETIME / 2)
    assert len(particles) == 1


def test_particle_removes_itself_once_expired(particles):
    Particle(100, 100).update(PARTICLE_LIFETIME)
    assert len(particles) == 0
