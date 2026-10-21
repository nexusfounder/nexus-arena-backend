import re

with open('app/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

routes = []
current_decorators = []

for idx, line in enumerate(lines):
    line_str = line.strip()
    if line_str.startswith('@app.'):
        current_decorators.append((idx + 1, line_str))
    elif current_decorators and (line_str.startswith('def ') or line_str.startswith('async def ')):
        fn_name = line_str.split('(')[0]
        params = line_str[len(fn_name):]
        routes.append({
            'line': current_decorators[0][0],
            'decorators': [d[1] for d in current_decorators],
            'func': fn_name + params[:80] + ('...' if len(params) > 80 else '')
        })
        current_decorators = []
    elif not line_str.startswith('@') and current_decorators:
        current_decorators = []

print(f"Total routes found: {len(routes)}")
for r in routes:
    # Check if route has Depends or auth
    dec_str = " ".join(r['decorators'])
    func_str = r['func']
    is_sensitive = any(word in func_str.lower() or word in dec_str.lower() for word in [
        'admin', 'withdraw', 'deposit', 'role', 'status', 'coin', 'payment', 'transfer', 'balance', 'reset', 'ban', 'delete'
    ])
    has_auth = 'get_current_user' in func_str or 'token' in func_str or 'verify' in func_str or 'admin' in func_str
    if is_sensitive:
        print(f"Line {r['line']}: {dec_str}")
        print(f"   Func: {func_str}")
        print(f"   Has Auth Clue: {has_auth}")
        print("-" * 50)
