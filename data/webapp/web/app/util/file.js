export class CSS {
    constructor() {
        this.head = document.querySelector('head');
    }
    load(file) {
        const link = document.createElement('link');
        link.setAttribute('href', file + '.css');
        link.setAttribute('rel', 'stylesheet');
        this.head.appendChild(link);
        return this;
    }
}

export class JS {
    constructor() {
        this.head = document.querySelector('head');
    }
    load(file) {
        const script = document.createElement('script');
        script.setAttribute('src', file + '.js');
        script.setAttribute('type', 'text/javascript');
        this.head.appendChild(script);
        return this;
    }
}