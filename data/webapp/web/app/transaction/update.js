import { Button, Panel } from "../plugin/mcontrol.js";
import { CardInfo } from "../classes/Card.js";
/* Concrete view */
export var UpdateView = function () {

    var content = new Panel();


    var card = new Button("Card", "success", "card")
        .addEventListener("click", function () {
            content.clear();
            content.add(new CardInfo('GSIS'));
        });



    return new Panel()
        .add(card)
        .add(content)
        .setStyle({
            padding: "10px"
        });
};

/* Concreate view */
