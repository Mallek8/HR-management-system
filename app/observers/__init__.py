"""
observers - Package implémentant le pattern Observer pour le système d'événements

Ce package fournit un système d'événements basé sur le pattern Observer,
permettant à différentes parties de l'application de réagir aux événements
sans être fortement couplées.

Design Pattern : Observer
- Subject : classe qui maintient une liste d'observateurs et les notifie des changements
- Observer : interface pour les classes qui souhaitent être notifiées
""" 