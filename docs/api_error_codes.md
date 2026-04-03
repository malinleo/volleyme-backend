# API Error Codes

This document lists every error code that can be returned by each API endpoint, split into **expected** (explicitly handled) and **unexpected** (unhandled, resulting in HTTP 500) errors.

---

## Error Handling Overview

The application registers the following FastAPI exception handlers:

| Exception class     | HTTP Status | Handler                          |
| ------------------- | ----------- | -------------------------------- |
| `UseCaseError`      | 400         | `handle_use_case_error`          |
| `NotFound`          | 404         | `handle_not_found_error`         |
| `Unauthorized`      | 401         | `handle_unauthorized_error`      |
| `PermissionDenied`  | 403         | `handle_permission_denied_error` |

Any exception **not** matching one of these (e.g. raw `DomainError`, `RepoError`) will result in an **HTTP 500 Internal Server Error**.

### Response format (for handled errors)

```json
{
  "details": [
    {
      "code": "<ERROR_CODE>",
      "messages": ["Human-readable message"],
      "fields": {
        "<field_name>": {
          "code": "<ERROR_CODE>",
          "messages": ["Field-level message"]
        }
      }
    }
  ]
}
```

---

## Authentication Dependency

All endpoints that require authentication (Events, Invitations) run the `authenticate_user` dependency, which invokes `AuthUseCase.execute()`. The following errors can be raised **before any endpoint logic runs**:

| Code                       | HTTP | Message                                       | Source              |
| -------------------------- | ---- | --------------------------------------------- | ------------------- |
| `__USE_CASE_ERROR__`       | 400  | Failed to authenticate                        | `AuthError` caught  |
| `__USE_CASE_NOT_FOUND__`   | 400  | User with given credentials wasn't found      | No auth user found  |

> Note: these use `UseCaseError` (not the `NotFound` subclass), so they return **400**, not 404.

---

## Auth API (`/auth`)

### `POST /auth/login/`

#### Expected errors

| Code                       | HTTP | Message                                       | Source                                        |
| -------------------------- | ---- | --------------------------------------------- | --------------------------------------------- |
| `__USE_CASE_ERROR__`       | 400  | Failed to authenticate                        | `AuthError` from auth strategy                |
| `__USE_CASE_NOT_FOUND__`   | 400  | User with given credentials wasn't found      | Auth strategy returned no user                |

#### Unexpected errors

| Source                                    | Potential error         |
| ----------------------------------------- | ----------------------- |
| `generate_auth_token_strategy.generate()` | Token generation failure |

---

### `POST /auth/register/`

#### Expected errors

| Code                                      | HTTP | Message                              | Source                                   |
| ----------------------------------------- | ---- | ------------------------------------ | ---------------------------------------- |
| `__USER_ALREADY_EXISTS__`                 | 400  | User with given email already exists | User query repo found existing user      |
| `__USE_CASE_PASSWORD_VALIDATION_FAILED__` | 400  | Password validation failed           | `PasswordValidator.validate()` failed    |
| `__USE_CASE_ERROR__`                      | 400  | Failed to register user              | `RepoError` from `user_repo.save_user`   |

`__USE_CASE_PASSWORD_VALIDATION_FAILED__` includes field-level details:

```json
{
  "fields": {
    "password": {
      "code": "__USE_CASE_PASSWORD_VALIDATION_FAILED__",
      "messages": ["<policy violation 1>", "<policy violation 2>"]
    }
  }
}
```

#### Unexpected errors

| Source                                    | Potential error          |
| ----------------------------------------- | ------------------------ |
| `generate_auth_token_strategy.generate()` | Token generation failure |

---

## Events API (`/events`)

> All endpoints require authentication. See [Authentication Dependency](#authentication-dependency) for auth-related errors.

### `GET /events/{event_id}/`

#### Expected errors

| Code                              | HTTP | Message                          | Source                                                   |
| --------------------------------- | ---- | -------------------------------- | -------------------------------------------------------- |
| `__USE_CASE_NOT_FOUND__`         | 404  | Event with id {id} not found     | Event not found in repo                                  |
| `__USE_CASE_NOT_FOUND__`         | 404  | Event with id {id} not found     | Event not visible and no invitation token provided       |
| `__INVALID_TOKEN__`              | 400  | Token is invalid                 | `ApplicationServiceError` from invitation token decode   |
| `__EXPIRED_TOKEN__`              | 400  | Token has expired                | `ApplicationServiceError` from invitation token decode   |
| `__USE_CASE_NOT_FOUND__`         | 404  | Invalid invitation token         | Invitation not found in repo by decoded token subject    |
| `EVENT_INVITATION_NOT_FOR_EVENT` | 400  | Event invitation not for given event | `DomainError` from `invitation.is_usable()` (see note)  |
| `EVENT_INVITATION_NOT_FOR_USER`  | 400  | Event invitation not for given user  | `DomainError` from `invitation.is_usable()` (see note)  |
| `EVENT_INVITATION_USED`          | 400  | Event invitation already used    | `DomainError` from `invitation.is_usable()` (see note)  |
| `EVENT_INVITATION_EXPIRED`       | 400  | Event invitation expired         | `DomainError` from `invitation.is_usable()` (see note)  |
| `__USE_CASE_NOT_FOUND__`         | 404  | Event with id {id} not found     | Event info query returned None after processing          |

> **Note:** `invitation.is_usable()` returns a `ValidationResult` and does not raise. The surrounding `try/except DomainError` block is effectively dead code. The invitation domain errors listed above will **not** actually be returned as 400 by this endpoint in the current implementation.

#### Unexpected errors

| Source                                            | Potential error                  |
| ------------------------------------------------- | -------------------------------- |
| `event_repo.get_event()`                          | `RepoError` / query failure      |
| `event_invitation_repo.get_invitation()`          | `RepoError` / query failure      |
| `event_invitation_repo.save_invitation()`         | `RepoError` / save failure       |
| `event_query_repo.get_event_info_for_user()`      | `RepoError` / query failure      |

---

### `GET /events/`

#### Expected errors

No endpoint-specific expected errors (only authentication dependency errors).

#### Unexpected errors

| Source                                              | Potential error             |
| --------------------------------------------------- | --------------------------- |
| `event_query_repo.get_events_info_for_user()`       | `RepoError` / query failure |

---

### `POST /events/`

#### Expected errors

| Code                       | HTTP | Message                              | Source                                               |
| -------------------------- | ---- | ------------------------------------ | ---------------------------------------------------- |
| `EVENT_END_BEFORE_START`   | 400  | Event end date must be after start date | `DomainError` from `Event.create()`               |
| `__USE_CASE_ERROR__`       | 400  | Failed to create event               | `RepoError` from `event_repo.save_event()`           |
| `__USE_CASE_NOT_FOUND__`   | 404  | Event with id {id} not found         | Event info query returned None after save            |

`EVENT_END_BEFORE_START` includes field-level details:

```json
{
  "fields": {
    "start_dt": {
      "code": "EVENT_END_BEFORE_START",
      "messages": ["Event end date must be after start date"]
    },
    "end_dt": {
      "code": "EVENT_END_BEFORE_START",
      "messages": ["Event end date must be after start date"]
    }
  }
}
```

#### Unexpected errors

| Source                                            | Potential error             |
| ------------------------------------------------- | --------------------------- |
| `event_query_repo.get_event_info_for_user()`      | `RepoError` / query failure |

---

### `POST /events/{event_id}/change-privacy/`

#### Expected errors

| Code                       | HTTP | Message                              | Source                                                  |
| -------------------------- | ---- | ------------------------------------ | ------------------------------------------------------- |
| `__USE_CASE_NOT_FOUND__`   | 404  | Event with id {id} not found         | Event not found in repo                                 |
| `EVENT_ALREADY_STARTED`    | 400  | Event already started                | `DomainError` from `make_public()` / `make_private()`   |
| `USER_NOT_HOST`            | 400  | User is not a host of the event      | `DomainError` from `make_public()` / `make_private()`   |
| `__USE_CASE_NOT_FOUND__`   | 404  | Event with id {id} not found         | Event info query returned None after save               |

#### Unexpected errors

| Source                                            | Potential error             |
| ------------------------------------------------- | --------------------------- |
| `event_repo.get_event()`                          | `RepoError` / query failure |
| `event_repo.save_event()`                         | `RepoError` / save failure  |
| `event_query_repo.get_event_info_for_user()`      | `RepoError` / query failure |

---

### `DELETE /events/{event_id}/`

#### Expected errors

| Code                              | HTTP | Message                                     | Source                                    |
| --------------------------------- | ---- | ------------------------------------------- | ----------------------------------------- |
| `__USE_CASE_NOT_FOUND__`         | 404  | Event with id {id} not found                | Event not found in repo                   |
| `__USE_CASE_VALIDATION_FAILED__` | 400  | Event is already started                    | `CanDeleteEventValidator`                 |
| `__USE_CASE_VALIDATION_FAILED__` | 400  | You are not allowed to delete this event    | `CanDeleteEventValidator`                 |
| `__USE_CASE_ERROR__`             | 400  | Failed to delete event                      | `RepoError` from `event_repo.delete_event()` |

#### Unexpected errors

| Source                    | Potential error             |
| ------------------------- | --------------------------- |
| `event_repo.get_event()`  | `RepoError` / query failure |

---

### `POST /events/{event_id}/join/`

#### Expected errors

| Code                              | HTTP | Message                                    | Source                                                |
| --------------------------------- | ---- | ------------------------------------------ | ----------------------------------------------------- |
| `__USE_CASE_NOT_FOUND__`         | 404  | Event with id {id} not found               | Event not found in repo                               |
| `__USE_CASE_NOT_FOUND__`         | 404  | Event with id {id} not found               | Event not visible and no invitation token provided    |
| `__INVALID_TOKEN__`              | 400  | Token is invalid                           | `ApplicationServiceError` from token decode           |
| `__EXPIRED_TOKEN__`              | 400  | Token has expired                          | `ApplicationServiceError` from token decode           |
| `__USE_CASE_NOT_FOUND__`         | 404  | Invalid invitation token                   | Invitation not found in repo                          |
| `EVENT_INVITATION_NOT_FOR_EVENT` | 400  | Event invitation not for given event       | `DomainError` from `invitation.use()`                 |
| `EVENT_INVITATION_NOT_FOR_USER`  | 400  | Event invitation not for given user        | `DomainError` from `invitation.use()`                 |
| `EVENT_INVITATION_USED`          | 400  | Event invitation already used              | `DomainError` from `invitation.use()`                 |
| `EVENT_INVITATION_EXPIRED`       | 400  | Event invitation expired                   | `DomainError` from `invitation.use()`                 |

#### Unexpected errors

| Source                                        | Potential error                                           |
| --------------------------------------------- | --------------------------------------------------------- |
| `event.add_participant()` -- `DomainError`    | `EVENT_ALREADY_STARTED`, `EVENT_ALREADY_FULL`, `USER_ALREADY_PARTICIPANT` |
| `event_repo.save_event()`                     | `RepoError` / save failure                                |
| `event_invitation_repo.save_invitation()`     | `RepoError` / save failure                                |
| `event_repo.get_event()`                      | `RepoError` / query failure                               |
| `event_invitation_repo.get_invitation()`      | `RepoError` / query failure                               |

> **Note:** `event.add_participant()` can raise `DomainError` with codes `EVENT_ALREADY_STARTED`, `EVENT_ALREADY_FULL`, and `USER_ALREADY_PARTICIPANT`, but these are **not** wrapped in a try/except and will result in HTTP 500.

---

### `POST /events/{event_id}/leave/`

#### Expected errors

| Code                              | HTTP | Message                                    | Source                         |
| --------------------------------- | ---- | ------------------------------------------ | ------------------------------ |
| `__USE_CASE_NOT_FOUND__`         | 404  | Event with id {id} not found               | Event not found in repo        |
| `__USE_CASE_VALIDATION_FAILED__` | 400  | You are a host of the event                | `CanLeaveEventValidator`       |
| `__USE_CASE_VALIDATION_FAILED__` | 400  | Event is already started                   | `CanLeaveEventValidator`       |
| `__USE_CASE_VALIDATION_FAILED__` | 400  | You are not a participant of the event     | `CanLeaveEventValidator`       |

#### Unexpected errors

| Source                                                | Potential error                                      |
| ----------------------------------------------------- | ---------------------------------------------------- |
| `event_aggregate.remove_participant()` -- `DomainError` | `EVENT_ALREADY_STARTED`, `USER_NOT_PARTICIPANT` (practically unreachable if validators pass) |
| `event_repo.save_event()`                             | `RepoError` / save failure                           |
| `event_repo.get_event()`                              | `RepoError` / query failure                          |

> **Note:** The validators check the same conditions as `remove_participant()`, so the `DomainError` is practically unreachable in normal flow. However, it could surface in a race condition.

---

## Invitations API (`/invitations`)

> All endpoints require authentication. See [Authentication Dependency](#authentication-dependency) for auth-related errors.

### `POST /invitations/`

#### Expected errors

| Code                              | HTTP | Message                              | Source                                                     |
| --------------------------------- | ---- | ------------------------------------ | ---------------------------------------------------------- |
| `__USE_CASE_NOT_FOUND__`         | 404  | Event with id {id} not found         | Event not found in repo                                    |
| `__USE_CASE_PERMISSION_DENIED__` | 403  | You are not a host of the event      | User is not a host of the event                            |
| *(from RepoError)*               | 400  | *(forwarded from repo error)*        | `RepoError` from `event_invitation_repo.save_invitation()` |

#### Unexpected errors

| Source                    | Potential error             |
| ------------------------- | --------------------------- |
| `event_repo.get_event()`  | `RepoError` / query failure |

---

## Error Code Reference

### Use Case Error Codes (`UseCaseErrorCode`)

| Enum member                    | String value                              |
| ------------------------------ | ----------------------------------------- |
| `DEFAULT`                      | `__USE_CASE_ERROR__`                      |
| `VALIDATION_FAILED`            | `__USE_CASE_VALIDATION_FAILED__`          |
| `NOT_FOUND`                    | `__USE_CASE_NOT_FOUND__`                  |
| `UNAUTHORIZED`                 | `__USE_CASE_UNAUTHORIZED__`               |
| `PERMISSION_DENIED`            | `__USE_CASE_PERMISSION_DENIED__`          |
| `PASSWORD_VALIDATION_FAILED`   | `__USE_CASE_PASSWORD_VALIDATION_FAILED__` |
| `USER_ALREADY_EXISTS`          | `__USER_ALREADY_EXISTS__`                 |

### Domain Error Codes (`domain.ErrorCode`)

| Enum member                       | String value                       |
| --------------------------------- | ---------------------------------- |
| `DEFAULT`                         | `DOMAIN_ERROR`                     |
| `EVENT_END_BEFORE_START`          | `EVENT_END_BEFORE_START`           |
| `EVENT_ALREADY_STARTED`           | `EVENT_ALREADY_STARTED`            |
| `EVENT_INVITATION_EXPIRED`        | `EVENT_INVITATION_EXPIRED`         |
| `EVENT_INVITATION_USED`           | `EVENT_INVITATION_USED`            |
| `EVENT_INVITATION_NOT_FOR_USER`   | `EVENT_INVITATION_NOT_FOR_USER`    |
| `EVENT_INVITATION_NOT_FOR_EVENT`  | `EVENT_INVITATION_NOT_FOR_EVENT`   |
| `EVENT_ALREADY_FULL`              | `EVENT_ALREADY_FULL`               |
| `USER_ALREADY_PARTICIPANT`        | `USER_ALREADY_PARTICIPANT`         |
| `USER_NOT_PARTICIPANT`            | `USER_NOT_PARTICIPANT`             |
| `USER_IS_HOST`                    | `USER_IS_HOST`                     |
| `USER_NOT_HOST`                   | `USER_NOT_HOST`                    |

### Application Service Error Codes (`ApplicationServiceErrorCode` / `AuthErrorCode`)

| Enum member       | String value                    |
| ----------------- | ------------------------------- |
| `DEFAULT`         | `__APPLICATION_SERVICE_ERROR__` |
| `INVALID_TOKEN`   | `__INVALID_TOKEN__`             |
| `EXPIRED_TOKEN`   | `__EXPIRED_TOKEN__`             |

### Repository Error Codes (`repos.ErrorCode`)

| Enum member      | String value        |
| ---------------- | ------------------- |
| `DEFAULT`        | `INFRA_ERROR`       |
| `REPO`           | `REPO_ERROR`        |
| `REPO_NOT_FOUND` | `REPO_NOT_FOUND`    |
| `REPO_SAVE`      | `REPO_SAVE_ERROR`   |
| `REPO_DELETE`     | `REPO_DELETE_ERROR`  |
| `REPO_QUERY`     | `REPO_QUERY_ERROR`  |
