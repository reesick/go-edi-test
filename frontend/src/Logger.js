/**
 * Behavior Logger - Tracks user interactions and sends to backend
 */

const BACKEND_URL = 'http://localhost:8080';

class Logger {
    constructor() {
        this.events = [];
    }

    logPause(stepIndex, duration) {
        const event = {
            type: 'pause',
            stepIndex,
            duration,
            timestamp: Date.now()
        };
        this.events.push(event);
        console.log('📊 Logged pause:', event);
    }

    logReplay(stepIndex) {
        const event = {
            type: 'replay',
            stepIndex,
            timestamp: Date.now()
        };
        this.events.push(event);
        console.log('📊 Logged replay:', event);
    }

    logHover(index) {
        const event = {
            type: 'hover',
            index,
            timestamp: Date.now()
        };
        this.events.push(event);
    }

    logScroll(depth) {
        const event = {
            type: 'scroll',
            depth,
            timestamp: Date.now()
        };
        this.events.push(event);
    }

    logSpeedChange(multiplier) {
        const event = {
            type: 'speed',
            multiplier,
            timestamp: Date.now()
        };
        this.events.push(event);
        console.log('📊 Logged speed change:', event);
    }

    getEvents() {
        return this.events;
    }

    clear() {
        this.events = [];
    }
}

export default new Logger();
