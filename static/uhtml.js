class e extends Map {
    set(e, t) {
        return super.set(e, t), t;
    }
}
class t extends WeakMap {
    set(e, t) {
        return super.set(e, t), t;
    }
}
/*! (c) Andrea Giammarchi - ISC */ const n =
        /^(?:area|base|br|col|embed|hr|img|input|keygen|link|menuitem|meta|param|source|track|wbr)$/i,
    r = /<([a-z]+[a-z0-9:._-]*)([^>]*?)(\/?)>/g,
    s = /([^\s\\>"'=]+)\s*=\s*(['"]?)\x01/g,
    l = /[\x01\x02]/g;
const o = (e, t) =>
        111 === e.nodeType
            ? 1 / t < 0
                ? t
                    ? (({ firstChild: e, lastChild: t }) => {
                          const n = document.createRange();
                          return n.setStartAfter(e), n.setEndAfter(t), n.deleteContents(), e;
                      })(e)
                    : e.lastChild
                : t
                ? e.valueOf()
                : e.firstChild
            : e,
    { isArray: a } = Array,
    i = (e) => (null == e ? e : e.valueOf()),
    c = (e, t) => {
        let n,
            r,
            s = t.slice(2);
        return (
            !(t in e) && (r = t.toLowerCase()) in e && (s = r.slice(2)),
            (t) => {
                const r = a(t) ? t : [t, !1];
                n !== r[0] &&
                    (n && e.removeEventListener(s, n, r[1]),
                    (n = r[0]) && e.addEventListener(s, n, r[1]));
            }
        );
    };
const { isArray: u, prototype: d } = Array,
    { indexOf: p } = d,
    {
        createDocumentFragment: f,
        createElement: h,
        createElementNS: m,
        createTextNode: g,
        createTreeWalker: y,
        importNode: b,
    } = new Proxy({}, { get: (e, t) => document[t].bind(document) });
let w;
const x = (e, t) =>
        t
            ? ((e) => {
                  w || (w = m('http://www.w3.org/2000/svg', 'svg')), (w.innerHTML = e);
                  const t = f();
                  return t.append(...w.childNodes), t;
              })(e)
            : ((e) => {
                  const t = h('template');
                  return (t.innerHTML = e), t.content;
              })(e),
    v = ({ childNodes: e }, t) => e[t],
    N = (e, t, n) =>
        ((e, t, n, r, s) => {
            const l = n.length;
            let o = t.length,
                a = l,
                i = 0,
                c = 0,
                u = null;
            for (; i < o || c < a; )
                if (o === i) {
                    const t = a < l ? (c ? r(n[c - 1], -0).nextSibling : r(n[a - c], 0)) : s;
                    for (; c < a; ) e.insertBefore(r(n[c++], 1), t);
                } else if (a === c)
                    for (; i < o; ) (u && u.has(t[i])) || e.removeChild(r(t[i], -1)), i++;
                else if (t[i] === n[c]) i++, c++;
                else if (t[o - 1] === n[a - 1]) o--, a--;
                else if (t[i] === n[a - 1] && n[c] === t[o - 1]) {
                    const s = r(t[--o], -1).nextSibling;
                    e.insertBefore(r(n[c++], 1), r(t[i++], -1).nextSibling),
                        e.insertBefore(r(n[--a], 1), s),
                        (t[o] = n[a]);
                } else {
                    if (!u) {
                        u = new Map();
                        let e = c;
                        for (; e < a; ) u.set(n[e], e++);
                    }
                    if (u.has(t[i])) {
                        const s = u.get(t[i]);
                        if (c < s && s < a) {
                            let l = i,
                                d = 1;
                            for (; ++l < o && l < a && u.get(t[l]) === s + d; ) d++;
                            if (d > s - c) {
                                const l = r(t[i], 0);
                                for (; c < s; ) e.insertBefore(r(n[c++], 1), l);
                            } else e.replaceChild(r(n[c++], 1), r(t[i++], -1));
                        } else i++;
                    } else e.removeChild(r(t[i++], -1));
                }
            return n;
        })(e.parentNode, t, n, o, e),
    C = (e, t) => {
        switch (t[0]) {
            case '?':
                return ((e, t, n) => (r) => {
                    const s = !!i(r);
                    n !== s && ((n = s) ? e.setAttribute(t, '') : e.removeAttribute(t));
                })(e, t.slice(1), !1);
            case '.':
                return ((e, t) =>
                    'dataset' === t
                        ? (
                              ({ dataset: e }) =>
                              (t) => {
                                  for (const n in t) {
                                      const r = t[n];
                                      null == r ? delete e[n] : (e[n] = r);
                                  }
                              }
                          )(e)
                        : (n) => {
                              e[t] = n;
                          })(e, t.slice(1));
            case '@':
                return c(e, 'on' + t.slice(1));
            case 'o':
                if ('n' === t[1]) return c(e, t);
        }
        switch (t) {
            case 'ref':
                return ((e) => {
                    let t;
                    return (n) => {
                        t !== n && ((t = n), 'function' == typeof n ? n(e) : (n.current = e));
                    };
                })(e);
            case 'aria':
                return ((e) => (t) => {
                    for (const n in t) {
                        const r = 'role' === n ? n : `aria-${n}`,
                            s = t[n];
                        null == s ? e.removeAttribute(r) : e.setAttribute(r, s);
                    }
                })(e);
        }
        return ((e, t) => {
            let n,
                r = !0;
            const s = document.createAttributeNS(null, t);
            return (t) => {
                const l = i(t);
                n !== l &&
                    (null == (n = l)
                        ? r || (e.removeAttributeNode(s), (r = !0))
                        : ((s.value = l), r && (e.setAttributeNodeNS(s), (r = !1))));
            };
        })(e, t);
    };
function A(e) {
    const { type: t, path: n } = e,
        r = n.reduceRight(v, this);
    return 'node' === t
        ? ((e) => {
              let t,
                  n,
                  r = [];
              const s = (l) => {
                  switch (typeof l) {
                      case 'string':
                      case 'number':
                      case 'boolean':
                          t !== l && ((t = l), n || (n = g('')), (n.data = l), (r = N(e, r, [n])));
                          break;
                      case 'object':
                      case 'undefined':
                          if (null == l) {
                              t != l && ((t = l), (r = N(e, r, [])));
                              break;
                          }
                          if (u(l)) {
                              (t = l),
                                  0 === l.length
                                      ? (r = N(e, r, []))
                                      : 'object' == typeof l[0]
                                      ? (r = N(e, r, l))
                                      : s(String(l));
                              break;
                          }
                          if (t !== l)
                              if ('ELEMENT_NODE' in l)
                                  (t = l),
                                      (r = N(e, r, 11 === l.nodeType ? [...l.childNodes] : [l]));
                              else {
                                  const e = l.valueOf();
                                  e !== l && s(e);
                              }
                          break;
                      case 'function':
                          s(l(e));
                  }
              };
              return s;
          })(r)
        : 'attr' === t
        ? C(r, e.name)
        : ((e) => {
              let t;
              return (n) => {
                  const r = i(n);
                  t != r && ((t = r), (e.textContent = null == r ? '' : r));
              };
          })(r);
}
const k = (e) => {
        const t = [];
        let { parentNode: n } = e;
        for (; n; ) t.push(p.call(n.childNodes, e)), (e = n), ({ parentNode: n } = e);
        return t;
    },
    $ = 'isµ',
    E = new t(),
    O = /^(?:textarea|script|style|title|plaintext|xmp)$/,
    T = (e, t) => {
        const o = 'svg' === e,
            a = ((e, t, o) => {
                let a = 0;
                return e
                    .join('')
                    .trim()
                    .replace(r, (e, t, r, l) => {
                        let a = t + r.replace(s, '=$2$1').trimEnd();
                        return l.length && (a += o || n.test(t) ? ' /' : '></' + t), '<' + a + '>';
                    })
                    .replace(l, (e) => ('' === e ? '\x3c!--' + t + a++ + '--\x3e' : t + a++));
            })(t, $, o),
            i = x(a, o),
            c = y(i, 129),
            u = [],
            d = t.length - 1;
        let p = 0,
            f = `${$}${p}`;
        for (; p < d; ) {
            const e = c.nextNode();
            if (!e) throw `bad template: ${a}`;
            if (8 === e.nodeType)
                e.data === f && (u.push({ type: 'node', path: k(e) }), (f = `${$}${++p}`));
            else {
                for (; e.hasAttribute(f); )
                    u.push({ type: 'attr', path: k(e), name: e.getAttribute(f) }),
                        e.removeAttribute(f),
                        (f = `${$}${++p}`);
                O.test(e.localName) &&
                    e.textContent.trim() === `\x3c!--${f}--\x3e` &&
                    ((e.textContent = ''),
                    u.push({ type: 'text', path: k(e) }),
                    (f = `${$}${++p}`));
            }
        }
        return { content: i, nodes: u };
    },
    S = (e, t) => {
        const { content: n, nodes: r } = E.get(t) || E.set(t, T(e, t)),
            s = b(n, !0);
        return { content: s, updates: r.map(A, s) };
    },
    L = (e, { type: t, template: n, values: r }) => {
        const s = M(e, r);
        let { entry: l } = e;
        (l && l.template === n && l.type === t) ||
            (e.entry = l =
                ((e, t) => {
                    const { content: n, updates: r } = S(e, t);
                    return { type: e, template: t, content: n, updates: r, wire: null };
                })(t, n));
        const { content: o, updates: a, wire: i } = l;
        for (let e = 0; e < s; e++) a[e](r[e]);
        return (
            i ||
            (l.wire = ((e) => {
                const { firstChild: t, lastChild: n } = e;
                if (t === n) return n || e;
                const { childNodes: r } = e,
                    s = [...r];
                return {
                    ELEMENT_NODE: 1,
                    nodeType: 111,
                    firstChild: t,
                    lastChild: n,
                    valueOf: () => (r.length !== s.length && e.append(...s), e),
                };
            })(o))
        );
    },
    M = ({ stack: e }, t) => {
        const { length: n } = t;
        for (let r = 0; r < n; r++) {
            const n = t[r];
            n instanceof j
                ? (t[r] = L(e[r] || (e[r] = { stack: [], entry: null, wire: null }), n))
                : u(n)
                ? M(e[r] || (e[r] = { stack: [], entry: null, wire: null }), n)
                : (e[r] = null);
        }
        return n < e.length && e.splice(n), n;
    };
class j {
    constructor(e, t, n) {
        (this.type = e), (this.template = t), (this.values = n);
    }
}
const B = (n) => {
        const r = new t();
        return Object.assign((e, ...t) => new j(n, e, t), {
            for(t, s) {
                const l = r.get(t) || r.set(t, new e());
                return (
                    l.get(s) ||
                    l.set(
                        s,
                        (
                            (e) =>
                            (t, ...r) =>
                                L(e, { type: n, template: t, values: r })
                        )({ stack: [], entry: null, wire: null }),
                    )
                );
            },
            node: (e, ...t) => L({ stack: [], entry: null, wire: null }, new j(n, e, t)).valueOf(),
        });
    },
    D = new t(),
    _ = (e, t) => {
        const n = 'function' == typeof t ? t() : t,
            r = D.get(e) || D.set(e, { stack: [], entry: null, wire: null }),
            s = n instanceof j ? L(r, n) : n;
        return s !== r.wire && ((r.wire = s), e.replaceChildren(s.valueOf())), e;
    },
    z = B('html'),
    H = B('svg');
export { j as Hole, z as html, _ as render, H as svg };
