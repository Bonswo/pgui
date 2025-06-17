# Pygame UI (pgui)
This package implements a small flexbox-like element that can be used to easily create UIs in pygame.

Requires Pygame-ce (version > 2.5)

Package comes with an `input` module which stores mouse position, updates elements' `hovered` property with
`input.update()`, and implements event listeners that can be subbed/unsubbed to with `input.sub(action, callback)`
and `input.unsub(action, callback)`.
