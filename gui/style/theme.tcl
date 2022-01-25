package require Tk 8.6

namespace eval ttk::theme::theme-dark {

    package provide ttk::theme::theme-dark

    variable colors
    array set colors {
        -background "#e7e7e7"
        -backgroundAlt "#383B3D"
        -gray51 "#808080"
        -foreground "#0C0D0E"
        -coolGray46 "#646695"
        -red51 "#f44747"
        -red59 "#ce7878"
        -orange70 "#d7ba7d"
        -green46 "#6A9955"
        -green73 "#b5cea8"
        -blue43 "#007ACC"
        -blue60 "#569cd6"
        -blue64 "#6796e6"
        -blue83 "#9cdcfe"
    }

    ::ttk::style theme create theme-dark -settings {

        # -----------------------------------------------------------------
        # defaults
        #
        ttk::style configure . \
            -background $colors(-background) \
            -foreground $colors(-foreground) \
            -troughcolor $colors(-background) \
            -focuscolor $colors(-blue43) \
            -selectbackground $colors(-blue43) \
            -selectforeground $colors(-foreground) \
            -insertcolor $colors(-foreground) \
            -insertwidth 1 \
            -fieldbackground $colors(-blue43) \
            -font {"Consolas" 12} \
            -borderwidth 0 \
            -padx 0 \
            -pady 0 \
            -relief flat \

        ttk::style map . -foreground [list disabled $colors(-foreground)]

        tk_setPalette background [ttk::style lookup . -background] \
        foreground [ttk::style lookup . -foreground] \
        highlightColor [ttk::style lookup . -focuscolor] \
        selectBackground [ttk::style lookup . -selectbackground] \
        selectForeground [ttk::style lookup . -selectforeground] \
        
        option add *font [ttk::style lookup . -font]
        option add *Menu.selectcolor $colors(-foreground)

        ## buttons
        ttk::style configure TButton -padding {2 2}
        ttk::style configure TButton -borderwidth 1
        ttk::style configure TButton -relief solid

        ## scrollbars
        ttk::style configure TScrollbar -padding {2 2}
        ttk::style configure TScrollbar -borderwidth 1
        ttk::style configure TScrollbar -relief solid
        ttk::style configure TScrollbar -width 18
        ttk::style configure TScrollbar -arrowsize 18

    }
}