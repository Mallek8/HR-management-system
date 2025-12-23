"""
event_subject.py - Implémentation du Sujet observé pour le pattern Observer

Ce module définit la classe EventSubject qui est le "Subject" dans le pattern Observer.
Cette classe maintient une liste d'observateurs et les notifie lorsqu'un événement se produit.

Design Pattern : Observer (composant "Subject")
- Maintient une liste d'observateurs
- Permet l'inscription et la désinscription des observateurs
- Notifie les observateurs lorsqu'un événement se produit
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Set, Optional
from app.observers.event_types import EventType


class Observer(ABC):
    """
    Interface pour les observateurs qui souhaitent être notifiés des événements.
    """
    
    @abstractmethod
    def update(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """
        Méthode appelée par le sujet lorsqu'un événement se produit.
        
        Args:
            event_type: Le type d'événement qui s'est produit
            data: Les données associées à l'événement
        """
        pass


class EventSubject:
    """
    Classe qui maintient une liste d'observateurs et les notifie des événements.
    C'est le "Subject" dans le pattern Observer.
    """
    
    _instance = None
    
    def __new__(cls):
        """
        Implémentation du pattern Singleton pour s'assurer qu'il n'y a qu'une seule
        instance d'EventSubject dans l'application.
        """
        if cls._instance is None:
            cls._instance = super(EventSubject, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialise la liste des observateurs par type d'événement.
        """
        if self._initialized:
            return
            
        self._observers: Dict[EventType, Set[Observer]] = {}
        self._callbacks: Dict[EventType, List[Callable]] = {}
        self._initialized = True
    
    def attach(self, observer: Observer, event_types: List[EventType] = None) -> None:
        """
        Ajoute un observateur à la liste pour les types d'événements spécifiés.
        
        Args:
            observer: L'observateur à ajouter
            event_types: Liste des types d'événements à observer (tous si None)
        """
        # Si aucun type d'événement n'est spécifié, attacher à tous les types
        if event_types is None:
            event_types = list(EventType)
        
        # Attacher l'observateur à chaque type d'événement
        for event_type in event_types:
            if event_type not in self._observers:
                self._observers[event_type] = set()
            self._observers[event_type].add(observer)
    
    def detach(self, observer: Observer, event_types: List[EventType] = None) -> None:
        """
        Retire un observateur de la liste pour les types d'événements spécifiés.
        
        Args:
            observer: L'observateur à retirer
            event_types: Liste des types d'événements à ne plus observer (tous si None)
        """
        # Si aucun type d'événement n'est spécifié, détacher de tous les types
        if event_types is None:
            event_types = list(EventType)
        
        # Détacher l'observateur de chaque type d'événement
        for event_type in event_types:
            if event_type in self._observers and observer in self._observers[event_type]:
                self._observers[event_type].remove(observer)
    
    def register_callback(self, event_type: EventType, callback: Callable) -> None:
        """
        Enregistre une fonction de rappel (callback) pour un type d'événement.
        
        Args:
            event_type: Le type d'événement auquel associer la fonction
            callback: La fonction à appeler lorsque l'événement se produit
        """
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)
    
    def unregister_callback(self, event_type: EventType, callback: Callable) -> None:
        """
        Supprime une fonction de rappel pour un type d'événement.
        
        Args:
            event_type: Le type d'événement
            callback: La fonction à supprimer
        """
        if event_type in self._callbacks and callback in self._callbacks[event_type]:
            self._callbacks[event_type].remove(callback)
    
    def notify(self, event_type: EventType, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Notifie tous les observateurs d'un événement.
        
        Args:
            event_type: Le type d'événement qui s'est produit
            data: Les données associées à l'événement
        """
        if data is None:
            data = {}
        
        # Notifier les observateurs
        if event_type in self._observers:
            for observer in self._observers[event_type]:
                try:
                    observer.update(event_type, data)
                except Exception as e:
                    # Log l'erreur mais ne pas interrompre les notifications
                    print(f"Erreur lors de la notification de l'observateur {observer}: {str(e)}")
        
        # Appeler les fonctions de rappel
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(event_type, data)
                except Exception as e:
                    # Log l'erreur mais ne pas interrompre les notifications
                    print(f"Erreur lors de l'appel du callback {callback}: {str(e)}") 