class Errors:

	GENERIC_ERROR = 'Si è verificato un errore, riprova più tardi'
	CANCEL = 'Cancellazione fallita'
	ALREADY_CANCELED = 'Cancellazione fallita, appuntamento già cancellato'
	CANCEL_ALREADY_COMPLETED = 'Cancellazione fallita, appuntamento già completato'
	DELETE = 'Eliminazione fallita'
	UPDATE = 'Aggiornamento fallito'
	PERMISSION_DENIED = 'Permesso negato'
	CAMPO_VUOTO = 'Campo da inserire mancante'

	LOGIN = 'Login fallito'
	REGISTER = 'Registrazione fallita'
	LOGOUT = 'Logout fallito'
	USER_DATA = 'Dati utente non validi'
	SESSION = 'Sessione scaduta'
	NOT_FOUND = 'Account non trovato'
	EMAIL_PASSWORD = 'Email o password non validi'
	EMAIL_EXISTS = 'Email già esistente'
	DIFFERENT_PASSWORDS = 'Le password non coincidono'
	PASSWORD_LENGTH = 'La password deve essere lunga almeno 8 caratteri'
	INVALID_USER = 'Utente non valido'
	NO_FEEDBACK = 'Nessuna recensione trovata'
	NO_IMAGE = 'Nessuna immagine trovata'

	BOOKED = 'Questo appuntamento è già stato prenotato'
	NEW_BOOKING = 'Errore creazione nuovo appuntamento'
	EDIT_BOOKING = 'Errore modifica appuntamento'
	NO_BOOKING = 'Nessun appuntamento trovato'
	INVALID_CONFIRMATION = 'Codice di conferma non valido'
	INVALID_BOOKING = 'Codice di prenotazione non valido'
	INVALID_NEW_BOOKING = 'Codice di generazione appuntamento non valido'
	INVALID_CONFIRM_EMAIL = 'Codice di conferma email non valido'
	INVALID_JOIN_ACCOUNT = 'Codice di unione account non valido'
	CONFIRM_BOOKING = 'Errore conferma appuntamento'
	ALREADY_CONFIRMED = 'Appuntamento già confermato'
	ALREADY_BOOKED = 'Appuntamento già prenotato'
	CONFIRM_BOOKING_NOT_BOOKED = 'Per confermare un appuntamento, lo stato deve essere "Prenotato"'
	ACCEPT_BOOKING_NOT_PENDING = 'Per accettare un appuntamento, lo stato deve essere "In attesa"'
	NEED_BOOKING_TO_FEEDBACK = 'Per inserire una recensione, devi aver completato un appuntamento'

	NO_DISCOUNT = 'Nessuno sconto disponibile'

	NO_MAIL = 'Nessuna mail da inviare'

	INVALID_RATING = 'Valutazione non valida, inserire un numero da 1 a 5'

	MISSING_FIELDS = 'Campi mancanti'

	INVALID_INPUT = 'Input {key} non valido per {value}'
	NO_INPUT = 'Input {key} non trovato'

	INVALID_REQUEST_NEW_BOOKING = 'Richiesta nuova prenotazione non valida'

	NO_USER = 'Utente non trovato'
	NO_COUPON = 'Coupon non trovato'

	INVALID_COUPON_COUNT = 'Valore coupon non valido: {value}. Inserire un valore tra 0 e 8'

	GET_CALENDAR = 'Errore recupero calendario'
	BOOK_BOOKING = 'Errore prenotazione appuntamento'
	GET_BOOKING = 'Errore recupero appuntamento'
	GET_BOOKINGS = 'Errore recupero appuntamenti'
	GET_BOOKING_INTERNAL_DATA = 'Errore recupero dati interni appuntamento'
	REQUEST_NEW_BOOKING = 'Errore richiesta nuova prenotazione'
	EDIT_BOOKING_INTERNAL_DATA = 'Errore modifica dati interni appuntamento'
	DELETE_BOOKING = 'Errore eliminazione appuntamento'
	ACCEPT_BOOKING = 'Errore accettazione appuntamento'
	GENERATE_NEW_BOOKING = 'Errore generazione nuova prenotazione'

	FORGOT_PASSWORD = 'Errore recupero password'
	RESTORE_PASSWORD = 'Errore ripristino password'
	INVALID_RESTORE_PASSWORD = 'Codice di ripristino password non valido'


class Messages:

	CANCEL = 'Cancellazione effettuata con successo'
	DELETE = 'Eliminazione effettuata con successo'
	UPDATE = 'Aggiornamento effettuato con successo'
	PERMISSION_GRANTED = 'Permesso concesso'

	LOGIN = 'Login effettuato con successo'
	REGISTER = 'Registrazione effettuata con successo'
	LOGOUT = 'Logout effettuato con successo'
	USER_DATA = 'Dati utente validi'
	SESSION = 'Nuova sessione creata'

	REQUEST_JOIN_ACCOUNT = 'Richiesta di unione account inviata con successo'
	SENDING_CONFIRM_MAIL = 'A breve riceverai una mail di conferma'

	BOOKED = 'Appuntamento prenotato con successo, a breve riceverai una mail di riepilogo'
	NEW_BOOKING = 'Nuovo appuntamento creato'
	EDIT_BOOKING = 'Appuntamento modificato con successo'
	EDIT_BOOKING_INTERNAL_DATA = 'Dati interni dell\'appuntamento modificati con successo'
	CONFIRM_BOOKING = 'Appuntamento confermato con successo'
	ACCEPT_BOOKING = 'Appuntamento prenotato con successo'
	COMPLETE_BOOKINGS = 'Appuntamenti completati con successo'

	DISCOUNT = 'Sconto disponibile'

	MAIL_BOOKING_REQUEST = 'Richiesta prenotazione di {name} {surname} per il {date} alle {start}'
	MAIL_BOOKING = 'Prenotazione LilivNails'
	MAIL_UPDATE = 'Aggiornamento appuntamento di {name} {surname}'
	MAIL_CANCEL = 'Cancellazione appuntamento di {name} {surname}'
	MAIL_CONFIRM = 'Conferma appuntamento LilivNails'
	MAIL_CONFIRM_EMAIL = 'Conferma email LilivNails'
	MAIL_JOIN_ACCOUNT = 'Unione account LilivNails'
	MAIL_NEW_BOOKING_REQUEST = 'Richiesta nuova prenotazione di {name} {surname} per il {date} alle {start}'
	MAIL_TIME = ' del {date} alle {start}'
	MAIL_RULES = 'Regolamento LilivNails'
	MAIL_GENERATE_NEW_BOOKING = 'Generazione nuova prenotazione'
	MAIL_FORGOT_PASSWORD = 'Recupero password LilivNails'

	ADDED_FEEDBACK = 'Recensione aggiunta con successo'

	CONFIRM = 'Conferma'
	ACCEPT = 'Accetta'
	REJECT = 'Rifiuta'
	ADD = 'Aggiungi'
	ADD_BOOKING = 'Aggiungi appuntamento'

	EMAIL_CONFIRMED = 'Email confermata con successo'
	JOIN_ACCOUNT = 'Account unito con successo, ora puoi accedere con le credenziali fornite'

	SENDED_NEW_REQUEST_BOOKING = 'Richiesta una nuova prenotazione a tuo nome, ti aggiorneremo appena possibile'

	REQUEST_NEW_BOOKING_SUCCESS = 'Generazione nuova prenotazione effettuata con successo'

	UPDATE_USER = 'Utente aggiornato con successo'

	FORGOT_PASSWORD = 'Email per il recupero password inviata con successo'
	RESTORE_PASSWORD = 'Password ripristinata con successo'
	RESTORE_PASSWORD_BUTTON = 'Ripristina password'


generic_error = {
	'status': False,
	'message': Errors.GENERIC_ERROR,
	'content': {}
}
