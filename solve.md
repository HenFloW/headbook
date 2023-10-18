_Henrik Flo Wilhelmsen (hwi038)_

## 2a

to be able to inject sql into the database we can put spesific textinput into the about field to escape the original sql, for example

```sql
x'; INSERT into users (username, password, info) VALUES ('xxx', 'ppp', '{}'); --
-- or update a user
x'; UPDATE users SET username = 'zzz' WHERE id = 3; --
-- and a more dangerous one
x'; UPDATE users SET password = 'hacked' WHERE id = 3 OR 1=1; --
```

this will escape the original sql and then you can add your own sql, this happens because the input is directly passed into the sql string and can change the structure of the sql query

to prevent this i will used prepared statement when i query the database with userinput, this will make sure that the input is not directly passed into the sql string and the structure will be the same

```py
def sql_execute(stmt, *args, **kwargs):
    debug(stmt, args or "", kwargs or "")

    return get_cursor().execute(stmt, (*args, ), **kwargs)
```

with this you also need do add ? to the original sql string where you want to add the userinput

```py
def get_user(userid):
        if type(userid) == int or userid.isnumeric():
            sql = f"SELECT id, username, password, info FROM users WHERE id = ?;"
        else:
            sql = f"SELECT id, username, password, info FROM users WHERE username = ?;"
        row = sql_execute(sql, userid).fetchone()
        if row:
            user = User(json.loads(row[3]))
            user.update({"id": row[0], "username": row[1], "password": row[2]})
            return user
```

## 2b

To be able to inject javascript into the homepage we can put spesific textinput into the about field, for example
inside about

```html
<img
    id="hack"
    src=""
    alt="hacked"
    style="
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    min-width: 100vw;
    min-height: 100vh;
    object-fit: cover;
    position: fixed;
    display: flex;
    z-index: 999;
  "
    onerror="
        document.getElementById(`hack`).src = `https://blackstormroofingmarketing.com/wp-content/uploads/2020/07/What-to-do-if-Your-Roofing-Website-is-hacked.gif`;
        document.body.style.backgroundColor = `black`;
        document.body.style.color = `green`;
        setTimeout(() => {
          alert(`Your website has been hacked!`)
        }, 100);
        "
/>
```

inside color

```html
green"></div>
<img
id="hack"
src=""
alt="hacked"
onerror="
  alert(`Your profile has been hacked!`)
  "
/>
<div style="
```

you can use a button with onlick to trigger the alert but with this method you can trigger the alert without clicking anything only rendering the img tag, in the color i can escape the html like we did in the sql injection and then i can put the img tag inside the div tag

this will inject javascript because the about input is directly passed to the innerHtml without any sanitization

```js
elt.innerHTML = `
        <img src="${user.picture_url || '/unknown.png'}" alt="${user.username + "'s profile picture"}">
        <div class="data">
            ${format_field('Name', user.username)}
            <div class="more">
                ${format_field('Birth date', user.birthdate)}
                ${format_field('Favourite colour', `${user.color} <div class="color-sample" style="${'background:'+user.color}"></div>`)}
                ${format_field('About', user.about, 'long')}
            </div>
        </div>
        <div class="controls">
```

to prevent this i made a function that sanitizes an input

```js
export const sanitizeInput = (input) => {
    const str = (input || '')
        .replace(/;/g, '&#059;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/=/g, '&#061;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    return str;
};
```

this will replace important characters with their html entities

by changing the format field i could use this function to sanitize the input, and to make it more dynamic i made a function that sanitizes all the fields by replacing ?0 ?1 ... with the sanitized inputs, i did this so you can add html inside the format_field value without having to escape each input manually

```js
export function format_field(key, value, options = {}, ...other) {
    // match for ?0, ?1, ?2, … in the value and replace with the corresponding argument
    // this lets me add HTML tags to the value wihout having to escape them everywhere
    const regex = /\?([0-9]+)/g;

    let match;
    while ((match = regex.exec(value))) {
        const index = parseInt(match[1]);
        value = value.replace(match[0]?.toString(), sanitizeInput(other[index]?.toString()));
    }
    // .....
    return `<li class="${classNames}"><span class="key">${key}</span>${value}</li>`;
}
```

example

```js
format_field(
    'Favourite colour',
    `?0<div class="color-sample" style="background:?0"></div>`,
    {},
    user.color,
);
format_field('About', '<i>?0</i>', 'long', user.about);
format_field('About', '<h1>?0</h1><p>?1</p>', 'long', user.username, user.about); // will sanitize both inputs before replacing them
```
