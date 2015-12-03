from decimal import Decimal
from mock import patch

from django.core import mail

from .mock_backend import DjrillBackendMockAPITestCase


class DjrillSessionSharingTests(DjrillBackendMockAPITestCase):
    """Test Djrill backend sharing of single Mandrill API connection"""

    @patch('requests.Session.close', autospec=True)
    def test_connection_sharing(self, mock_close):
        """Djrill reuses one requests session when sending multiple messages"""
        datatuple = (
            ('Subject 1', 'Body 1', 'from@example.com', ['to@example.com']),
            ('Subject 2', 'Body 2', 'from@example.com', ['to@example.com']),
        )
        mail.send_mass_mail(datatuple)
        self.assertEqual(self.mock_post.call_count, 2)
        session1 = self.mock_post.call_args_list[0][0]  # arg[0] (self) is session
        session2 = self.mock_post.call_args_list[1][0]
        self.assertEqual(session1, session2)
        self.assertEqual(mock_close.call_count, 1)

    @patch('requests.Session.close', autospec=True)
    def test_caller_managed_connections(self, mock_close):
        """Calling code can created long-lived connection that it opens and closes"""
        connection = mail.get_connection()
        connection.open()
        mail.send_mail('Subject 1', 'body', 'from@example.com', ['to@example.com'], connection=connection)
        session1 = self.mock_post.call_args[0]
        self.assertEqual(mock_close.call_count, 0)  # shouldn't be closed yet

        mail.send_mail('Subject 2', 'body', 'from@example.com', ['to@example.com'], connection=connection)
        self.assertEqual(mock_close.call_count, 0)  # still shouldn't be closed
        session2 = self.mock_post.call_args[0]
        self.assertEqual(session1, session2)  # should have reused same session

        connection.close()
        self.assertEqual(mock_close.call_count, 1)

    def test_session_closed_after_exception(self):
        # fail loud case:
        msg = mail.EmailMessage('Subject', 'Message', 'from@example.com', ['to1@example.com'],)
        msg.global_merge_vars = {'PRICE': Decimal('19.99')}  # will cause JSON serialization error
        with patch('requests.Session.close', autospec=True) as mock_close:
            with self.assertRaises(TypeError):
                msg.send()
        self.assertEqual(mock_close.call_count, 1)

        # fail silently case (EmailMessage caches backend on send, so must create new one):
        msg = mail.EmailMessage('Subject', 'Message', 'from@example.com', ['to1@example.com'],)
        msg.global_merge_vars = {'PRICE': Decimal('19.99')}
        with patch('requests.Session.close', autospec=True) as mock_close:
            sent = msg.send(fail_silently=True)
            self.assertEqual(sent, 0)
        self.assertEqual(mock_close.call_count, 1)

        # caller-supplied connection case:
        with patch('requests.Session.close', autospec=True) as mock_close:
            connection = mail.get_connection()
            connection.open()
            msg = mail.EmailMessage('Subject', 'Message', 'from@example.com', ['to1@example.com'],
                                    connection=connection)
            msg.global_merge_vars = {'PRICE': Decimal('19.99')}
            with self.assertRaises(TypeError):
                msg.send()
            self.assertEqual(mock_close.call_count, 0)  # wait for us to close it

            connection.close()
            self.assertEqual(mock_close.call_count, 1)
