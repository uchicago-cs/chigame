
Here are the fixtures for Knowledge Base. Assume makemigrations are up-to-date.

## Pls run this command in the root directory:

```python manage.py loaddata src/chigame/knowledge_base/fixtures/kb_user_game_data.json src/chigame/knowledge_base/fixtures/kb_guides_data.json src/chigame/knowledge_base/fixtures/kb_feedbacks_data.json```


## The fixture contains the following info:
### Users:
| pk | Name  | Email             | Moderator |
|----|-------|-------------------|-----------|
| 1  | Admin | admin@example.com | True      |
| 2  | Alex  | alex@example.com  | True      |
| 3  | Sam   | sam@example.com   | False     |
| 4  | Alice | alice@example.com | False     |

With all the passwords being: **test12345**

Only Admin and Alex are moderators.

### Game
| pk | Game     | published_guide_id |
|----|----------|--------------------|
| 1  | Chess    | 1                |
| 2  | Go Game  | 2                |
| 3  | Game A   | N/A                |


### Guide
| pk | Author             | Game     | Status   | Likes/Favorites |
|----|------------------|----------|----------|------------------|
| 1  | Alice     | Chess    | Approved (Published) | N/A              |
| 2  | Admin      | Go Game  | Approved (Published)  | 2 (Alex, Sam)/1 (Admin)             |
| 3  | Sam  | Chess   | Approved (NOT published)    |     N/A         |
| 4  | Alice  | Game A   | Pending    |     N/A         |
| 5  | Alex  | Go Game   | Pending    |     N/A         |
| 6  | Sam  | Go Game   | Requested Change    |     N/A         |
| 7  | Sam  | Game A   | Rejected    |     N/A         |

As suggested from the Game table above, only guide 1 and 2 are published, to Chess and Go Game respectively.

### ReviewFeedback
| pk | reviewer | guide_id | status   |
|----|----------|----------|----------|
| 1  | Admin    | 1        | Requested Change |
| 2  | Alex     | 2        | Approved  |
| 3  | Admin      | 3        | Approved |
| 4  | Admin    | 6        | Requested Change |
| 5  | Alex    | 7        | Rejected |
| 6  | Admin    | 1        | Approved |

As this table suggests, the guide 1 has been requested change and then approved.
