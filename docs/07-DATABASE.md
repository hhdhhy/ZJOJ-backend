# 鏁版嵁搴撹�璁?
> 馃梽锔?ZJOJ 鏁版嵁搴撴牳蹇冭�璁℃�瑙?
---

## 鏁版嵁搴撶幆澧?
- **绫诲瀷**: MySQL 8.0
- **瀛楃�闆?*: utf8mb4
- **寮曟搸**: InnoDB
- **鐢ㄦ埛妯″瀷**: 鑷�畾涔?OJUser (uid 涓轰富閿?

---

## 鏍稿績鏁版嵁琛?
### 1. 鐢ㄦ埛妯″潡

#### ojauth_ojuser锛堢敤鎴疯〃锛?
| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| uid | VARCHAR(22) | Short UUID 涓婚敭 |
| username | VARCHAR(150) | 鐢ㄦ埛鍚嶏紙鍞�竴锛?|
| email | VARCHAR(254) | 閭��锛堢櫥褰曡处鍙凤紝鍞�竴锛?|
| telephone | VARCHAR(20) | 鎵嬫満鍙凤紙鍞�竴锛?|
| realname | VARCHAR(150) | 鐪熷疄濮撳悕 |
| password | VARCHAR(128) | 瀵嗙爜鍝堝笇 |
| role | INT | 瑙掕壊锛?-瀛︾敓, 2-鏁欑粌, 3-绠＄悊鍛?|
| is_superuser | TINYINT | 鏄�惁瓒呯骇鐢ㄦ埛 |
| is_staff | TINYINT | 鏄�惁宸ヤ綔浜哄憳 |
| status | INT | 鐘舵€侊細1-婵€娲? 2-鏈�縺娲? 3-閿佸畾 |
| avatar | VARCHAR(200) | 澶村儚URL |
| bio | TEXT | 涓�汉绠€浠?|
| date_joined | DATETIME | 娉ㄥ唽鏃堕棿 |

**鐗圭偣**锛?- 浣跨敤 Short UUID 閬垮厤淇℃伅娉勯湶
- 閭��浣滀负鐧诲綍璐﹀彿
- PBKDF2 鍔犲瘑瀛樺偍瀵嗙爜
- 鏀�寔涓夌�瑙掕壊锛氬�鐢熴€佹暀缁冦€佺�鐞嗗憳

---

### 2. 棰樼洰妯″潡

#### problem_problem锛堥�鐩�〃锛?
| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| problem_id | VARCHAR(20) | 棰樼洰缂栧彿锛堜富閿�紝濡?P1001锛?|
| title | VARCHAR(100) | 棰樼洰鏍囬� |
| description | LONGTEXT | 棰樼洰鎻忚堪锛圡arkdown锛?|
| time_limit | INT | 鏃堕棿闄愬埗锛堟�绉掞級 |
| memory_limit | INT | 鍐呭瓨闄愬埗锛圡B锛?|
| creator_id | VARCHAR(255) | 鍒涘缓鑰咃紙澶栭敭锛孲ET NULL锛?|

#### problem_tag锛堟爣绛捐〃锛?
| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | BIGINT | 鑷��涓婚敭 |
| name | VARCHAR(50) | 鏍囩�鍚嶏紙鍞�竴锛?|

**鍏崇郴**锛歅roblem 鈫?Tag锛堝�瀵瑰�锛?
---

### 3. 鎻愪氦璁板綍妯″潡

#### submission锛堟彁浜よ〃锛?
| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | BIGINT | 鑷��涓婚敭 |
| problem_id | VARCHAR(20) | 棰樼洰锛堝�閿�級 |
| user_id | VARCHAR(255) | 鐢ㄦ埛锛堝�閿�級 |
| language | VARCHAR(20) | 缂栫▼璇�█锛坈pp/c/java/python3锛?|
| code | LONGTEXT | 鎻愪氦鐨勪唬鐮?|
| code_length | INT | 浠ｇ爜闀垮害锛堝瓧鑺傦級 |
| status | INT | 璇勬祴鐘舵€侊紙0-4锛?|
| result | VARCHAR(10) | 璇勬祴缁撴灉锛圓C/WA/TLE绛夛級 |
| score | INT | 寰楀垎 |
| execution_time | INT | 杩愯�鏃堕棿锛堟�绉掞級 |
| memory_usage | INT | 鍐呭瓨浣跨敤锛圞B锛?|
| submit_time | DATETIME | 鎻愪氦鏃堕棿 |
| judge_time | DATETIME | 璇勬祴鏃堕棿 |

**璇勬祴鐘舵€?*锛?- 0: 绛夊緟璇勬祴
- 1: 璇勬祴涓?- 2: 宸插畬鎴?- 3: 缂栬瘧閿欒�
- 4: 绯荤粺閿欒�

**璇勬祴缁撴灉**锛?- AC: Accepted锛堥€氳繃锛?- WA: Wrong Answer锛堢瓟妗堥敊璇�級
- TLE: Time Limit Exceeded锛堣秴鏃讹級
- MLE: Memory Limit Exceeded锛堣秴鍐呭瓨锛?- RE: Runtime Error锛堣繍琛岄敊璇�級
- CE: Compilation Error锛堢紪璇戦敊璇�級
- SE: System Error锛堢郴缁熼敊璇�級

#### test_case_result锛堟祴璇曠偣缁撴灉琛�級

| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | BIGINT | 鑷��涓婚敭 |
| submission_id | BIGINT | 鎻愪氦璁板綍锛堝�閿�級 |
| test_case_id | INT | 娴嬭瘯鐢ㄤ緥ID |
| status | VARCHAR(10) | 娴嬭瘯鐐圭姸鎬侊紙AC/WA/TLE/MLE/RE锛?|
| execution_time | INT | 鐢ㄦ椂锛堟�绉掞級 |
| memory_usage | INT | 鍐呭瓨锛圞B锛?|
| score | INT | 璇ユ祴璇曠偣寰楀垎 |
| message | TEXT | 璇︾粏淇℃伅 |

---

### 4. 鐝�骇绠＄悊妯″潡

#### ojauth_class锛堢彮绾ц〃锛?
| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | BIGINT | 鑷��涓婚敭 |
| name | VARCHAR(100) | 鐝�骇鍚嶇О锛堝敮涓€锛?|
| coach_id | VARCHAR(22) | 鐝�富浠?鏁欑粌锛堝�閿�紝SET NULL锛?|
| description | TEXT | 鐝�骇鎻忚堪 |
| create_time | DATETIME | 鍒涘缓鏃堕棿 |

#### ojauth_class_member锛堢彮绾ф垚鍛樿〃锛?
| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | BIGINT | 鑷��涓婚敭 |
| class_obj_id | BIGINT | 鐝�骇锛堝�閿�級 |
| user_id | VARCHAR(22) | 瀛︾敓锛堝�閿�級 |
| join_time | DATETIME | 鍔犲叆鏃堕棿 |

**鍏崇郴**锛?- Class 鈫?OJUser (coach): 澶氬�涓€
- Class 鈫?OJUser (members): 澶氬�澶氾紙閫氳繃 ClassMember锛?
---

### 5. AI 鍔╂墜妯″潡

#### ai_assistant_knowledgebase锛堢煡璇嗗簱锛?
| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | BIGINT | 鑷��涓婚敭 |
| title | VARCHAR(200) | 鏂囨。鏍囬� |
| content | LONGTEXT | 鏂囨。鍐呭� |
| embedding | JSON | 鍚戦噺宓屽叆 |
| problem_id | VARCHAR(20) | 鍏宠仈棰樼洰锛堝彲閫夛級 |

#### ai_assistant_chathistory锛堝�璇濆巻鍙诧級

| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | BIGINT | 鑷��涓婚敭 |
| user_id | VARCHAR(255) | 鐢ㄦ埛锛堝�閿�級 |
| messages | JSON | 瀵硅瘽娑堟伅鍒楄〃 |
| created_at | DATETIME | 鍒涘缓鏃堕棿 |

#### ai_assistant_userprofile锛堢敤鎴稟I閰嶇疆锛?
| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | BIGINT | 鑷��涓婚敭 |
| user_id | VARCHAR(22) | 鐢ㄦ埛锛堜竴瀵逛竴锛?|
| api_key | VARCHAR(255) | 鐢ㄦ埛鑷�畾涔?API Key |
| model | VARCHAR(50) | 鍋忓ソ妯″瀷 |

#### ai_assistant_ratelimit锛堥�鐜囬檺鍒讹級

| 瀛楁� | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | BIGINT | 鑷��涓婚敭 |
| user_id | VARCHAR(22) | 鐢ㄦ埛锛堝�閿�級 |
| request_count | INT | 浠婃棩璇锋眰娆℃暟 |
| last_request | DATETIME | 鏈€鍚庤�姹傛椂闂?|

---

## ER 鍏崇郴鍥?
```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?      鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹? OJUser      鈹?      鈹?  Problem       鈹?鈹傗攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?      鈹傗攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?uid (PK)     鈹傗梽鈹€鈹€鈹€鈹€鈹€鈹€鈹?creator_id (FK) 鈹?鈹?username     鈹?      鈹?problem_id (PK) 鈹?鈹?email        鈹?      鈹?title           鈹?鈹?role         鈹?      鈹?description     鈹?鈹?telephone    鈹?      鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹�攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹�攢鈹€鈹€鈹€鈹€鈹€鈹€鈹?               鈹?       鈹?                       鈹?       鈹?             鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?  Submission     鈹?       鈹?             鈹傗攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?id (PK)          鈹?       鈹?             鈹?user_id (FK)     鈹?       鈹?             鈹?problem_id (FK)  鈹?       鈹?             鈹?result           鈹?       鈹?             鈹?code             鈹?       鈹?             鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹�攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?                      鈹?       鈹?             鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?TestCaseResult        鈹?       鈹?             鈹傗攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?submission_id (FK)    鈹?       鈹?             鈹?test_case_id          鈹?       鈹?             鈹?result                鈹?       鈹?             鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?       鈹?             鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?  Class              鈹?       鈹?             鈹傗攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?id (PK)              鈹?       鈹?             鈹?coach_id (FK) 鈼勨攢鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?name                 鈹?       鈹?             鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹�攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?                      鈹?       鈹?             鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?ClassMember           鈹?       鈹?             鈹傗攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?class_obj_id (FK)     鈹?       鈹?             鈹?user_id (FK) 鈼勨攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?       鈹?             鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?ChatHistory          鈹?       鈹?             鈹傗攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?             鈹?user_id (FK)         鈹?       鈹?             鈹?messages (JSON)      鈹?       鈹?             鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

---

## 绱㈠紩浼樺寲寤鸿�

### 蹇呭缓绱㈠紩

1. **鐢ㄦ埛琛?*锛歶sername, email, telephone锛堝敮涓€绱㈠紩锛?2. **棰樼洰琛?*锛歱roblem_id锛堜富閿�級
3. **鎻愪氦琛?*锛歶ser_id, problem_id, submit_time锛堣仈鍚堟煡璇�紭鍖栵級
4. **娴嬭瘯鐐圭粨鏋?*锛歴ubmission_id锛堝�閿�煡璇�級
5. **鐝�骇琛?*锛歯ame锛堝敮涓€绱㈠紩锛?6. **鐝�骇鎴愬憳**锛歝lass_obj_id, user_id锛堣仈鍚堝敮涓€绱㈠紩锛?
### 鎬ц兘浼樺寲

1. **鍒嗛〉鏌ヨ�**锛氬湪 submit_time 涓婂缓绔嬬储寮?2. **鏍囩�绛涢€?*锛歱roblem_tag 涓�棿琛ㄥ缓绔嬭仈鍚堢储寮?3. **鎼滅储鍔熻兘**锛氳€冭檻浣跨敤鍏ㄦ枃绱㈠紩鎴?Elasticsearch

---

## 娉ㄦ剰浜嬮」

1. **澶栭敭绾︽潫**锛歝reator_id銆乧oach_id 浣跨敤 SET NULL锛屽垹闄ょ敤鎴锋椂淇濈暀鏁版嵁
2. **澶у瓧娈?*锛歞escription銆乧ode銆乧ontent銆乥io 浣跨敤 LONGTEXT/TEXT
3. **JSON 瀛楁�**锛歮essages銆乪mbedding 浣跨敤 JSON 绫诲瀷锛圡ySQL 5.7+锛?4. **鏃堕棿鎴?*锛氫娇鐢?DATETIME(6) 鏀�寔寰��绮惧害
5. **鍞�竴鎬?*锛氱彮绾у悕绉板叏灞€鍞�竴锛岄伩鍏嶉噸澶?
---

## 鐩稿叧鏂囦欢

- 鐢ㄦ埛妯″瀷锛歚apps/ojauth/models.py`
- 棰樼洰妯″瀷锛歚apps/problem/models.py`
- 鎻愪氦妯″瀷锛歚apps/problem/models.py`锛圫ubmission, TestCaseResult锛?- AI 妯″瀷锛歚apps/ai_assistant/models.py`
- 鏉冮檺绯荤粺鏂囨。锛歚docs/06-MODULES/permission-system.md`
