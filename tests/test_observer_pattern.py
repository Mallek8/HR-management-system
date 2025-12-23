import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

from app.observers.event_subject import EventSubject, Observer
from app.observers.event_types import EventType
from app.services.event_service import EventService


class TestObserver(Observer):
    """Observateur de test pour vérifier le pattern Observer."""
    
    def __init__(self):
        self.last_event_type = None
        self.last_data = None
        self.update_count = 0
    
    def update(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Implémentation de la méthode update de l'interface Observer."""
        self.last_event_type = event_type
        self.last_data = data
        self.update_count += 1


@pytest.fixture
def reset_event_subject():
    """Fixture pour réinitialiser le singleton EventSubject entre les tests."""
    # Sauvegarde l'instance actuelle
    old_instance = EventSubject._instance
    
    # Réinitialise l'instance
    EventSubject._instance = None
    
    yield
    
    # Restaure l'instance d'origine après le test
    EventSubject._instance = old_instance


def test_event_subject_singleton(reset_event_subject):
    """Test du pattern Singleton dans EventSubject."""
    subject1 = EventSubject()
    subject2 = EventSubject()
    
    # Vérifier que c'est la même instance
    assert subject1 is subject2


def test_event_subject_attach_detach(reset_event_subject):
    """Test des méthodes attach et detach d'EventSubject."""
    subject = EventSubject()
    observer = TestObserver()
    
    # Attacher l'observateur
    subject.attach(observer, [EventType.LEAVE_APPROVED])
    
    # Vérifier que l'observateur est bien attaché
    assert observer in subject._observers[EventType.LEAVE_APPROVED]
    
    # Détacher l'observateur
    subject.detach(observer, [EventType.LEAVE_APPROVED])
    
    # Vérifier que l'observateur est bien détaché
    assert observer not in subject._observers[EventType.LEAVE_APPROVED]


def test_event_subject_notify(reset_event_subject):
    """Test de la méthode notify d'EventSubject."""
    subject = EventSubject()
    observer = TestObserver()
    
    # Attacher l'observateur
    subject.attach(observer, [EventType.LEAVE_APPROVED])
    
    # Données de test
    test_data = {"employee_id": 1, "start_date": "2023-01-01", "end_date": "2023-01-05"}
    
    # Notifier l'observateur
    subject.notify(EventType.LEAVE_APPROVED, test_data)
    
    # Vérifier que l'observateur a bien été notifié
    assert observer.update_count == 1
    assert observer.last_event_type == EventType.LEAVE_APPROVED
    assert observer.last_data == test_data


def test_event_subject_callback(reset_event_subject):
    """Test des callbacks dans EventSubject."""
    subject = EventSubject()
    callback_mock = MagicMock()
    
    # Enregistrer le callback
    subject.register_callback(EventType.LEAVE_APPROVED, callback_mock)
    
    # Données de test
    test_data = {"employee_id": 1, "start_date": "2023-01-01", "end_date": "2023-01-05"}
    
    # Notifier
    subject.notify(EventType.LEAVE_APPROVED, test_data)
    
    # Vérifier que le callback a été appelé
    callback_mock.assert_called_once_with(EventType.LEAVE_APPROVED, test_data)
    
    # Désenregistrer le callback
    subject.unregister_callback(EventType.LEAVE_APPROVED, callback_mock)
    
    # Réinitialiser le mock et notifier à nouveau
    callback_mock.reset_mock()
    subject.notify(EventType.LEAVE_APPROVED, test_data)
    
    # Vérifier que le callback n'a pas été appelé
    callback_mock.assert_not_called()


def test_event_service_emit_event(reset_event_subject):
    """Test de la méthode emit_event du EventService."""
    observer = TestObserver()
    
    # Enregistrer l'observateur via le service
    EventService.register_observer(observer, [EventType.LEAVE_APPROVED])
    
    # Données de test
    test_data = {"employee_id": 1, "start_date": "2023-01-01", "end_date": "2023-01-05"}
    
    # Émettre un événement
    EventService.emit_event(EventType.LEAVE_APPROVED, test_data)
    
    # Vérifier que l'observateur a bien été notifié
    assert observer.update_count == 1
    assert observer.last_event_type == EventType.LEAVE_APPROVED
    assert observer.last_data == test_data


def test_event_service_unregister_observer(reset_event_subject):
    """Test de la méthode unregister_observer du EventService."""
    observer = TestObserver()
    
    # Enregistrer puis désenregistrer l'observateur
    EventService.register_observer(observer, [EventType.LEAVE_APPROVED])
    EventService.unregister_observer(observer, [EventType.LEAVE_APPROVED])
    
    # Émettre un événement
    EventService.emit_event(EventType.LEAVE_APPROVED, {"test": "data"})
    
    # Vérifier que l'observateur n'a pas été notifié
    assert observer.update_count == 0


def test_event_service_specialized_emit_methods(reset_event_subject):
    """Test des méthodes d'émission spécialisées du EventService."""
    with patch('app.services.event_service.EventService.emit_event') as mock_emit:
        # Émettre un événement de demande de congé
        EventService.emit_leave_requested(
            employee_id=1,
            supervisor_id=2,
            start_date="2023-01-01",
            end_date="2023-01-05"
        )
        
        # Vérifier l'appel à emit_event
        mock_emit.assert_called_once()
        args, kwargs = mock_emit.call_args
        assert args[0] == EventType.LEAVE_REQUESTED
        assert args[1]["employee_id"] == 1
        assert args[1]["supervisor_id"] == 2
        assert args[1]["start_date"] == "2023-01-01"
        assert args[1]["end_date"] == "2023-01-05"


def test_event_service_initialize(reset_event_subject):
    """Test de la méthode initialize du EventService."""
    # Au lieu de mocker NotificationObserver, surveiller directement la méthode attach du sujet
    with patch.object(EventSubject, 'attach') as mock_attach:
        # Initialiser le service d'événements
        EventService.initialize()
        
        # Vérifier que la méthode attach a été appelée au moins une fois
        assert mock_attach.called, "EventSubject.attach devrait être appelé pendant l'initialisation"
        
        # Vérifier que le premier argument de l'appel est bien un NotificationObserver
        first_call_args = mock_attach.call_args[0]
        assert len(first_call_args) >= 1, "attach devrait recevoir au moins un argument"
        
        # Vérifier que le premier argument est bien une instance de Observer
        assert isinstance(first_call_args[0], Observer), "Le premier argument devrait être un Observer" 