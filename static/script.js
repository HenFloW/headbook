import { render, html } from '/uhtml.js';

/**
 * Wrapper around fetch() for JSON data
 *
 * @param {*} path The path (or URL)
 * @param {*} method Request method, defaults to GET
 * @param {*} headers Additional headers
 * @returns The response data, as an object, or null if the request failed
 */
export async function fetch_json(path, method = 'GET', headers = {}) {
    const resp = await fetch(path, {
        method,
        headers: {
            accept: 'application/json',
            ...headers,
        },
    });
    if (resp.ok) {
        return await resp.json();
    } else {
        console.error('Request failed:', resp.status, resp.statusText);
        return null;
    }
}

/**
 * Get list of users from server
 *
 * @returns A list of simple user objects (only id and username)
 */
export async function list_users() {
    return (await fetch_json('/users')) || [];
}

/**
 * Get a user profile from the server
 * @param {*} userid The numeric user id
 * @returns A user object
 */
export async function get_profile(userid) {
    return await fetch_json(`/users/${userid}`);
}

/**
 * Format a key-value field
 *
 * @param {*} key The key
 * @param {*} value The value
 * @param {*} options Object with options {optional: bool, className: string, long: bool}
 * @returns HTML text
 */
export function format_field(key, value, options = {}) {
    if (options.optional && !value) return '';
    let classNames = 'field';

    if (options.className)
        // if we need extra styling
        classNames = `${classNames} ${options.className}`;
    if (options.long)
        // if the value is a longer text
        classNames = `${classNames} long`;
    const val = options.long
        ? html`<div class="value">${value || ''}</div>`
        : html` <span class="value">${value || ''}</span>`;
    return html`<li class="${classNames}"><span class="key">${key}</span>${val}</li>`;
}

/**
 * Display a user as a HTML element
 *
 * @param {*} user A user object
 * @param {*} elt An optional element to render the user into
 * @returns elt or a new element
 */
export async function format_profile(user, elt) {
    // added this route so you could not set the user id from the console to bypass the security
    window.current_user_id = await fetch_json('/current_user_id', 'GET');

    if (!elt) elt = document.createElement('div');
    elt.classList.add('user'); // set CSS class
    if (user.id == current_user_id) {
        // current_user_id is a global variable (set on 'window')
        elt.classList.add('me');
    }

    // get friendship status
    const friendship_status = await fetch_json(`/buddies/${user.id}`, 'GET');

    // if not friends, this will show
    let more = html`<i>Become friends with ${user.username} to see their profile</i>`;

    if (
        friendship_status.status == 'friends' ||
        user.id == current_user_id ||
        friendship_status.status == 'requested'
    ) {
        // get the rest of the profile
        more = html`
            ${format_field('Birth date', user.birthdate)}
            ${format_field(
                'Favourite colour',
                html`${user.color}
                    <div class="color-sample" style="${'background:' + user.color}"></div>`,
            )}
            ${format_field('About', user.about, 'long')}
        `;
    }

    render(
        elt,
        html`
            <img
                src="${user.picture_url || '/unknown.png'}"
                alt="${user.username + "'s profile picture"}"
            />
            <div class="data">
                ${format_field('Name', user.username)}
                <div class="more">${more}</div>
            </div>
            <div class="controls"> ${await generate_friendship_controls(user)} </div>
        `,
    );
    return elt;
}

const action_enum = {
    add_request: 'add_request',
    cancel_request: 'cancel_request',
    accept_request: 'accept_request',
    reject_request: 'reject_request',
    remove_friend: 'remove_friend',
};

const generate_friendship_controls = async (user) => {
    window.current_user_id = await fetch_json('/current_user_id', 'GET');

    if (!user.id) return html``;
    if (user.id == current_user_id) return html``;

    const response = await fetch_json(`/buddies/${user.id}`, 'GET');

    const friendship_status = response.status;

    if (!friendship_status) return html``;

    if (user.id == window.current_user_id) return html``;

    let text = 'Add as buddy';
    let action = action_enum.add_request;

    if (friendship_status == 'pending') {
        text = 'Pending...';
        action = action_enum.cancel_request;
    }
    if (friendship_status == 'friends') {
        text = 'Remove buddy';
        action = action_enum.remove_friend;
    }
    if (friendship_status == 'requested') {
        return html`<button type="button" data-action="${action_enum.accept_request}"
                >Accept</button
            >
            <button type="button" data-action="${action_enum.reject_request}">Reject</button>`;
    }

    return html`<button type="button" data-action="${action}">${text}</button>`;
};

/**
 * Perform an action, such as a button click.
 *
 * Get the action to perform and any arguments from the 'data-*' attributes on the button element.
 *
 * @param {*} element A button element with `data-action="…"` set
 * @returns true if action was performed
 */
export async function do_action(id, element) {
    let did_action = false;
    let response = {};
    if ([action_enum.add_request, action_enum.accept_request].includes(element.dataset.action)) {
        response = await fetch_json(`/buddies/${id}`, 'POST', {
            action: element.dataset.action,
        });
        did_action = true;
    }
    if (
        [
            action_enum.reject_request,
            action_enum.cancel_request,
            action_enum.remove_friend,
        ].includes(element.dataset.action)
    ) {
        response = await fetch_json(`/buddies/${id}`, 'DELETE', {
            action: element.dataset.action,
        });
        did_action = true;
    }

    if (did_action) {
        if (response.ok) {
            const button = await generate_friendship_controls({ id });
            const controls = element.parentElement;
            if (button && controls) {
                render(controls, button);
            }
        }
    }
    return did_action;
}
// demo of uhtml templates
function uhtml_demo() {
    const main = document.querySelector('main');
    function show_demo(name, template) {
        console.log(name, simple_tmpl);
        const elt = document.createElement('div');
        main.appendChild(elt);
        render(elt, html`<h3>${name}</h3>${template}`);
    }
    const unsafe_data = '<script>alert()</script>';
    // safely inserted as a string
    const simple_tmpl = html`<em>${unsafe_data}</em>`;
    show_demo('simple_tmpl', simple_tmpl);

    const username = 'foo',
        nested = 'nested';
    const user = html`<em>${username}</em>`;
    // nested templates are inserted as HTML elements
    const message_tmpl = html`<div
        >Hello, my name is ${user}, and your name is ${html`<b>${nested}</b>`}</div
    >`;
    show_demo('message_tmpl', message_tmpl);

    const users = ['alice', 'bob'];
    // you can also use lists
    const users_tmpl = html`<ul
        >${users.map((user) => html`<li>${user}</li>`)}</ul
    >`;
    show_demo('users_tmpl', users_tmpl);

    const color = 'red';
    // attributes require special care
    const attr_tmpl = html`<div class="color-sample" style="${'background:' + color}"></div>`;
    show_demo('attr_tmpl', attr_tmpl);

    // this won't work
    const attr_tmpl_err = html`<div class="color-sample" style="background: ${color}"></div>`;
    try {
        show_demo('attr_tmpl_err', attr_tmpl_err);
    } catch (e) {
        console.error(e);
    }
}

window.uhtml_demo = uhtml_demo;

function createElement_demo() {
    function element(tag, { cssClass, child } = {}) {
        const elt = document.createElement(tag);
        if (cssClass) elt.className = cssClass;
        if (typeof child === 'string' || typeof child === 'number') elt.innerText = `${child}`;
        else if (child) elt.appendChild(text);
        return elt;
    }

    const fields = [
        { key: 'Name', value: 'alice' },
        { key: 'Favourite color', value: 'pink' },
    ];
    const outerDiv = element('div', { cssClass: 'data' });
    fields.forEach((field) => {
        const item = element('li', { cssClass: 'field' });
        item.appendChild(element('span', { cssClass: 'key', child: field.key }));
        item.appendChild(element('span', { cssClass: 'value', child: field.value }));
        outerDiv.appendChild(item);
    });
    document.querySelector('main').appendChild(element('h3', { child: 'createElement demo' }));
    document.querySelector('main').appendChild(outerDiv);
}
window.createElement_demo = createElement_demo;
