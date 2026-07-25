**Implementing RS3TK GUI**

We need to implement various RuneScape API's for use in the new UI
    
---

**/playerDetails.ws**
    Example Request:
        https://secure.runescape.com/m=website-data/playerDetails.ws?names=["User0","User1"]]&callback=jQuery000000000000000_0000000000&_=0
    Example Response:
        ```
        jQuery000000000000000_0000000000([{"isSuffix":false,"recruiting":true,"name":"User0","clan":"Cabbages","title":""},{"isSuffix":false,"name":"User1","title":""}]); 
        ```
        
---

**RuneMetrics**
    Example Request:
        https://apps.runescape.com/runemetrics/profile/profile?user=User0&activities=5
    Example Response:
        ```
        {
            "magic": 19884227,
            "questsstarted": 4,
            "totalskill": 3027,
            "questscomplete": 288,
            "questsnotstarted": 71,
            "totalxp": 1285110912,
            "ranged": 113597283,
            "activities": [
                {
                "date": "18-Jul-2026 19:05",
                "details": "Completing That Old Black Magic has given me enough Quest Points to pass the 400 QP milestone.",
                "text": "400 Quest Points obtained"
                },
                {
                "date": "18-Jul-2026 19:05",
                "details": "I helped to reunite the City of Um's jazz band.",
                "text": "Quest complete: That Old Black Magic"
                },
                {
                "date": "18-Jul-2026 18:47",
                "details": "By levelling up my Archaeology skill, I achieved at least level 69 in all skills.",
                "text": "Levelled all skills over 69"
                },
                {
                "date": "18-Jul-2026 18:47",
                "details": "I levelled my Archaeology skill, I am now level 69.",
                "text": "Levelled up Archaeology."
                },
                {
                "date": "18-Jul-2026 16:37",
                "details": "I killed 16 Hermods, Spirits of War: phantoms born from the God Wars.",
                "text": "I killed 16 Hermods."
                }
            ],
            "skillvalues": [
                {
                "level": 120,
                "xp": 1445285876,
                "rank": 23450,
                "id": 24
                },
                {
                "level": 99,
                "xp": 1135972838,
                "rank": 56475,
                "id": 3
                },
                {
                "level": 120,
                "xp": 1059825754,
                "rank": 25890,
                "id": 2
                },
                {
                "level": 119,
                "xp": 1026986679,
                "rank": 76642,
                "id": 18
                },
                {
                "level": 119,
                "xp": 1015801507,
                "rank": 51398,
                "id": 6
                },
                {
                "level": 120,
                "xp": 997548208,
                "rank": 79381,
                "id": 26
                },
                {
                "level": 119,
                "xp": 948308217,
                "rank": 47375,
                "id": 4
                },
                {
                "level": 116,
                "xp": 755539043,
                "rank": 68589,
                "id": 17
                },
                {
                "level": 110,
                "xp": 396301807,
                "rank": 73296,
                "id": 14
                },
                {
                "level": 99,
                "xp": 344109409,
                "rank": 68634,
                "id": 10
                },
                {
                "level": 108,
                "xp": 320548575,
                "rank": 76664,
                "id": 0
                },
                {
                "level": 107,
                "xp": 301101505,
                "rank": 74143,
                "id": 8
                },
                {
                "level": 106,
                "xp": 271768731,
                "rank": 116421,
                "id": 19
                },
                {
                "level": 99,
                "xp": 236217012,
                "rank": 58285,
                "id": 7
                },
                {
                "level": 99,
                "xp": 227281061,
                "rank": 64140,
                "id": 25
                },
                {
                "level": 104,
                "xp": 226166477,
                "rank": 74632,
                "id": 21
                },
                {
                "level": 99,
                "xp": 223105457,
                "rank": 128376,
                "id": 1
                },
                {
                "level": 103,
                "xp": 213757754,
                "rank": 88793,
                "id": 11
                },
                {
                "level": 99,
                "xp": 208020386,
                "rank": 85886,
                "id": 16
                },
                {
                "level": 103,
                "xp": 201396526,
                "rank": 72343,
                "id": 22
                },
                {
                "level": 99,
                "xp": 198842276,
                "rank": 73304,
                "id": 5
                },
                {
                "level": 102,
                "xp": 190616556,
                "rank": 155610,
                "id": 15
                },
                {
                "level": 102,
                "xp": 186444490,
                "rank": 83518,
                "id": 20
                },
                {
                "level": 102,
                "xp": 178629813,
                "rank": 100777,
                "id": 12
                },
                {
                "level": 102,
                "xp": 175765692,
                "rank": 113385,
                "id": 13
                },
                {
                "level": 99,
                "xp": 165722584,
                "rank": 75557,
                "id": 23
                },
                {
                "level": 101,
                "xp": 164185584,
                "rank": 100117,
                "id": 9
                },
                {
                "level": 83,
                "xp": 28832723,
                "rank": 189407,
                "id": 28
                },
                {
                "level": 69,
                "xp": 7026721,
                "rank": 252750,
                "id": 27
                }
            ],
            "name": "User0",
            "rank": "89,607",
            "melee": 653710728,
            "combatlevel": 151,
            "loggedIn": "false"
        }
        ```

**Player Count**
    Example Request:
        https://www.runescape.com/player_count.js?varname=iPlayerCount&callback=jQuery000000000000000_0000000000&_=0
    Example Response:
        ```
        jQuery000000000000000_0000000000(152835);
        ```
        
**Player Avatar**
    Example Request:
        https://secure.runescape.com/m=avatar-rs/User0/chat.png
    Example Response:
        Redirect -> 'https://secure.runescape.com/m=avatar-rs/avatar.png?id=00000000'
        Redirect -> 'https://secure.runescape.com/m=avatar-rs/default_chat.png?'
