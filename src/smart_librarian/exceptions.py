class SmartLibrarianError(Exception):
    """Base exception for application-specific errors."""


class ConfigurationError(SmartLibrarianError):
    """Raised when required application configuration is invalid."""


class DataFileError(SmartLibrarianError):
    """Raised when the local dataset cannot be loaded."""


class DuplicateBookTitleError(DataFileError):
    """Raised when multiple books use the same title."""


class VectorStoreError(SmartLibrarianError):
    """Raised when an operation involving the vector database fails."""


class BookNotFoundError(SmartLibrarianError):
    """Raised when a requested book title does not exist."""
