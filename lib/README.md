# Overview

# Installation

# Project structure

## Classes

### `Bus`

# Potential design problems
- If we consider `boarding_rate` and `alight_rate`, the bus may take too long to alight people and demand will increase until it fills up the bus, which sometimes happen, but sometimes it doesn't and it could be unnecesarily slow. However, that aside, we should consider carefully the distribution of demand across ticks, since boarding could also take forever if demand is not controlled (a time limit could be set depending on demand, for example).