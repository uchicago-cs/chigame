
Here are the fixtures for Knowledge Base. Assume makemigrations are up-to-date.

## Setup

To load the knowledge base filter, please run the following command in the root
of the project

```python manage.py loaddata src/chigame/knowledge_base/fixtures/kb_user_game_data.json src/chigame/knowledge_base/fixtures/kb_guides_data.json src/chigame/knowledge_base/fixtures/kb_feedbacks_data.json src/chigame/knowledge_base/fixtures/kb_email_verifications_data```


## Fixture Contents
### Users
| pk | Name  | Email             | Moderator | Email Verified |
|----|-------|-------------------|-----------|----------------|
| 1  | Admin | admin@example.com | True      | True           |
| 2  | Alex  | alex@example.com  | True      | True           |
| 3  | Sam   | sam@example.com   | False     | True           |
| 4  | Alice | alice@example.com | False     | True           |

All users have the password: **test12345**

Only Admin and Alex are moderators.

### Games
| pk | Game     | published_guide_id | Categories                 |
|----|----------|--------------------|----------------------------|
| 1  | Chess    | 1                  | Abstract Stategy, Ancient  |
| 2  | Go Game  | 2                  | Abstract Strategy          |
| 3  | Game A   | N/A                | Educational                |


### Guides
| pk | Author             | Game   | Status                 | Likes/Favorites         |
|----|------------------|----------|------------------------|-------------------------|
| 1  | Alice            | Chess    | Approved (Published)   | N/A                     |
| 2  | Admin            | Go Game  | Approved (Published)   | 2 (Alex, Sam)/1 (Admin) |
| 3  | Sam              | Chess    | Approved (Unpublished) | N/A                     |
| 4  | Alice            | Game A   | Pending                | N/A                     |
| 5  | Alex             | Go Game  | Pending                | N/A                     |
| 6  | Sam              | Go Game  | Requested Change       | N/A                     |
| 7  | Sam              | Game A   | Rejected               | N/A                     |

As suggested from the Game table above, only guide 1 and 2 are published, to Chess and Go Game respectively.

### Review Feedback
| pk | reviewer | guide_id | status           |
|----|----------|----------|------------------|
| 1  | Admin    | 1        | Requested Change |
| 2  | Alex     | 2        | Approved         |
| 3  | Admin    | 3        | Approved         |
| 4  | Admin    | 6        | Requested Change |
| 5  | Alex     | 7        | Rejected         |
| 6  | Admin    | 1        | Approved         |

As this table suggests, the guide 1 has been requested change and then approved.
