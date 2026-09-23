import json
with open('prompts.json', encoding='utf-8') as f:
    for line in f:
        p = json.loads(line)
        if p.get('company_id') == '209cb85e-5ce7-449e-b32c-ad5ca4c6c635':
            with open('test_prompt.txt', 'w', encoding='utf-8') as out:
                out.write(p.get('welcome_message', ''))
