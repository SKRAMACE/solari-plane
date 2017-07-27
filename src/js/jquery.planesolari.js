// FlapBuffer constructor
var FlapBuffer = function(wrap, num_lines) {
    this.wrap = wrap;
    this.num_lines = num_lines;
    this.line_buffer = '';
    this.buffers = [[]];
    this.cursor = 0;
};

// FlapBuffer Methods
FlapBuffer.prototype = {

    pushLine: function(line) {

        if (this.buffers[this.cursor].length < this.num_lines) {
           this.buffers[this.cursor].push(line);
        } else {
            this.buffers.push([]);
            this.cursor++;
            this.pushLine(line);
        } 
    },

    pushWord: function(word) {
        if (this.line_buffer.length == 0) {
            this.line_buffer = word;
        } else if ((word.length + this.line_buffer.length + 1) <= this.wrap) {
            this.line_buffer += ' ' + word;
        } else {
            this.pushLine(this.line_buffer);
            this.line_buffer = word;
        }
    },

    flush: function() {
        if (this.line_buffer.length) {
            this.pushLine(this.line_buffer);
            this.line_buffer = '';
        }
    },

};

// Solari prototype
var Solari = function(display_selector, data_selector, input_selector, update_selector) {
    var _this = this;

    var onAnimStart = function(e) {
        var $display = $(e.target);
        $display.prevUntil('.flapper', '.activity').addClass('active');

        // Start playing audio when the first bank starts
        if (anim_active == 0) {
            console.log('Starting: ' + anim_active);
            anim_sound.play();
        };

        // Keep track of active banks
        anim_active += 1;
    };

    var onAnimEnd = function(e) {
        var $display = $(e.target);
        $display.prevUntil('.flapper', '.activity').removeClass('active');

        // Keep track of active banks
        anim_active -= 1;

        // Stop playing audio when the last bank stops
        if (anim_active == 0) {
            console.log("Stopping: " + anim_active);
            anim_sound.pause();
            anim_sound.currentTime = 0;
        };
    };

    var _width = (function() {
        // For some reason, this breaks the indicator light
        var w = $(window).width()/(30+8);
        return 38;
    })();

    this.opts = {
        chars_preset: 'alphanum',
        align: 'left',
        width: _width,
        on_anim_start: onAnimStart,
        on_anim_end: onAnimEnd
    };

    var anim_active = 0;
    var anim_sound = new Audio('split_flap.mp3');

    this.timers = [];

    this.$displays = $(display_selector);
    this.num_lines = this.$displays.length;

    this.line_delay = 300;
    this.screen_delay = 7000;

    this.$displays.flapper(this.opts);

    this.$data_input = $(data_selector);
    this.$html_input = $(input_selector);

    $(update_selector).get(function(e){
        var solari_data = _this.$data_input.data('solari_data')
        var text;
        text = _this.cleanInput(solari_data);
        //text = _this.cleanInput(_this.$html_input.html());
        var buffers = _this.parseInput(text);

        _this.stopDisplay();
        _this.updateDisplay(buffers);

        e.preventDefault();
    });

    this.update = function() {
        var solari_data = _this.$data_input.data('solari_data')
        var text;
        text = _this.cleanInput(solari_data);
        //text = _this.cleanInput(_this.$html_input.html());
        var buffers = _this.parseInput(text);

        _this.stopDisplay();
        _this.updateDisplay(buffers);
    }
};

// Solari methods
Solari.prototype = {

    cleanInput: function(text) {
        return text.toUpperCase();
    },

    parseInput: function(text) {
        var buffer = new FlapBuffer(this.opts.width, this.num_lines);
        var lines = text.split(/\n/);

        for (i in lines) {
            var words = lines[i].split(/\s/);
            for (j in words) {
                buffer.pushWord(words[j]);
            }
            buffer.flush();
        }

        buffer.flush();
        return buffer.buffers;
    },

    stopDisplay: function() {
        for (i in this.timers) {
            clearTimeout(this.timers[i]);
        }

        this.timers = [];
    },

    updateDisplay: function(buffers) {
        var _this = this;
        var timeout = 100;

        for (i in buffers) {

            _this.$displays.each(function(j) {

                var $display = $(_this.$displays[j]);

                (function(i,j) {
                    _this.timers.push(setTimeout(function(){
                        if (buffers[i][j]) {
                            $display.val(buffers[i][j]).change();
                        } else {
                            $display.val('').change();
                        }
                    }, timeout));
                } (i, j));

                timeout += _this.line_delay;
            });

            timeout += _this.screen_delay;
        }
    }

};

// Entry point
//  This runs when the DOM is ready for JavaScript to run
$(document).ready(function(){
    var display_selector = 'input.display';
    var data_selector = '#flapper_section';
    var input_selector = '#div2';
    var update_selector = '#showme';
    var refresh_interval = 5000

    // Stash a key-value pair in element 
    $(data_selector).data('solari_data', 'init'); 

    // Instantiate object
    solari = new Solari(display_selector, data_selector, input_selector, update_selector);

    // Run handleInverval every refresh_interval milliseconds
    setInterval(function(){ handleInterval() },refresh_interval);

    solari.update()

    var Fields = function() {
        this.flight = 7;
        this.tofrom = 20;
        this.time = 5;
        this.gate = 4;
    };

    function fmt_field(data, len) {
        console.log(data)
        console.log(len)
        console.log(data.length)
        var _data = data.substring(0, Math.min(len, data.length))
        console.log(_data)
        var field_pad = len - _data.length
        _data += Array(field_pad + 1).join(" ")
        console.log(_data)
        return _data + " "
    }

    function fmt_data(data) {
        var f = new Fields();

        var _data = 'Arrivals\n'
        console.log('Arrivals')
        for (i in data.arrivals) {
            x = data.arrivals[i]
            console.log(x)
            var flight = x.carrier + x.flight
            _data += fmt_field(flight, f.flight);
            _data += fmt_field(x.tofrom, f.tofrom);
            _data += fmt_field(x.sched, f.time);
            _data += fmt_field(x.gate, f.gate);
            _data += "\n"
        }
    }

    // Success callback
    function apply_get(data) {
        var _data = 'Arrivals\n'
        console.log('Arrivals')
        for (i in data.arrivals) {
            x = data.arrivals[i]
            console.log(x)
            var flight = x.carrier + x.flight
            _data += flight + '\n'
            _data += x.tofrom + '\n'
            _data += x.sched + '\n'
            _data += x.gate + '\n'
            _data += "\n"
        }

        for (i in data.departures) {
            x = data.departures[i]
            console.log(x)
            _data += x.carrier + x.flight + " "
            _data += x.tofrom + " "
            _data += x.sched + " "
            _data += x.gate + " "
            _data += "\n"
        }
        console.log(_data);

        // Update selectors
        $(data_selector).data('solari_data', String(_data));
        $(input_selector).html(_data);

        // Update object
        solari.update()
    }
        
    // Query data every INTERVAL seconds
    function handleInterval() {
        // TODO: Config file
        var _url = 'http://localhost:5000/planesolari/api/v1.0/flights'
        $.ajax({url:_url, success: apply_get, cache: false});
    }
});
