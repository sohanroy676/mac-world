# Project Brief

## Overview

This project extends OSCAR, a deep-reinforcement-learning approach for IEEE 802.11 contention-window optimization, from a single-AP setup to a multi-AP network.

The project uses ns-3, ns3-gym, and DDPG-based Actor-Critic agents.

## Core Goal

Build a multi-AP OSCAR system where:

- multiple APs run in one ns-3 simulation
- each AP has an independent AP-level Actor-Critic agent
- each AP has its own contention window
- agents use only their local information
- APs can have different numbers of stations
- the system scales from 2 APs toward at least 10 APs
- W&B tracks experiments

## v1 Success

The initial v1 milestone is a working two-AP implementation with:

- AP-specific observations
- AP-specific rewards
- AP-specific CW control
- independent AP agents
- working ns3-gym communication
- successful training
- W&B experiment tracking
- baseline validation

The centralized critic is a later phase.

## Main Evaluation

The primary performance metric is throughput.

Other relevant metrics include:

- per-AP throughput
- aggregate throughput
- fairness
- reward
- loss/collision-related measurements
- CW behavior
- convergence
- training/runtime cost

## Out of Scope for v1

- Mobility
- Dynamic station addition
- Detailed AP interference modeling
- Per-station Actor agents
- Centralized critic as part of the initial implementation