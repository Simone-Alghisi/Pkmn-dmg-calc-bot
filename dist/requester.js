"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var calc_1 = require("@smogon/calc");
var fs_1 = require("fs");
var path_1 = require("path");
//call the function to calculate
calculateDamage();
function calculateDamage() {
    var fileName = process.argv[2];
    var folderName = process.argv[3];
    var destinationFolderName = process.argv[4];
    if (fileName !== undefined && folderName !== undefined && destinationFolderName !== undefined) {
        var jsonPath = path_1.join(__dirname, '..', folderName, fileName);
        var obj = JSON.parse(fs_1.readFileSync(jsonPath, 'utf8'));
        var attacker = obj.attacker;
        var defender = obj.defender;
        var move = obj.move;
        var field = obj.field;
        var gen = calc_1.Generations.get(8);
        if (field.terrain !== undefined && field.terrain === "None") {
            field.terrain = undefined;
        }
        if (field.weather !== undefined && field.weather === "None") {
            field.weather = undefined;
        }
        var validity = isDataValid(move.name, attacker, defender);
        var isCalculable = validity[0];
        var errorMessage = validity[1];
        var text_result = "";
        try {
            if (isCalculable) {
                var result = calc_1.calculate(gen, new calc_1.Pokemon(gen, attacker.name, attacker.args), new calc_1.Pokemon(gen, defender.name, defender.args), new calc_1.Move(gen, move.name, move), new calc_1.Field(field));
                text_result = printValidResult(result);
            }
            else {
                text_result = errorMessage;
            }
        }
        catch (error) {
            console.log(error);
            text_result = "An unexpected error occurred, if the problem persists please contact @Alghisius";
        }
        var resultPath = path_1.join(__dirname, '..', destinationFolderName, fileName);
        fs_1.writeFileSync(resultPath, text_result);
    }
    else {
        console.log("wrong number of argument passed");
    }
}
function printValidResult(result) {
    var rawDesc = result.rawDesc;
    var damage = result.damage;
    var defenderHP = result.defender.originalCurHP;
    var text_result = result.fullDesc();
    if (damage !== undefined && typeof (damage) === 'object') {
        text_result += "\nPossible damage amounts: (";
        for (var i = 0; i < damage.length; i++) {
            text_result += damage[i];
            if (i + 1 < damage.length) {
                text_result += ", ";
            }
        }
        text_result += ")";
    }
    return text_result;
}
function isDataValid(move, attacker, defender) {
    var isCalculable = true;
    var errorMessage = "ERORR: ";
    if (attacker === undefined || defender === undefined) {
        isCalculable = false;
        errorMessage += "One of the Pokémon was 'undefined'";
    }
    if (isCalculable) {
        var isAttackerPkmn = false;
        var isDefenderPkmn = false;
        var specie = calc_1.SPECIES[calc_1.SPECIES.length - 1];
        if (specie[attacker.name] !== undefined) {
            isAttackerPkmn = true;
        }
        if (specie[defender.name] !== undefined) {
            isDefenderPkmn = true;
        }
        if (!isAttackerPkmn || !isDefenderPkmn) {
            isCalculable = false;
            errorMessage += defender.name + " or " + attacker.name + " are not Pokémon Species";
        }
    }
    if (isCalculable) {
        var items = calc_1.ITEMS[calc_1.ITEMS.length - 1];
        var attackerItem = attacker.args.item;
        var defenderItem = defender.args.item;
        var isAttackerItemValid = attackerItem === undefined ? true : false;
        var isDefenderItemValid = defenderItem === undefined ? true : false;
        var i = 0;
        while ((!isAttackerItemValid || !isDefenderItemValid) && i < items.length) {
            if (!isAttackerItemValid && items[i] === attackerItem) {
                isAttackerItemValid = true;
            }
            if (!isDefenderItemValid && items[i] === defenderItem) {
                isDefenderItemValid = true;
            }
            i++;
        }
        if (!isAttackerItemValid || !isDefenderItemValid) {
            isCalculable = false;
            errorMessage += attackerItem + " or " + defenderItem + " are not valid Items";
        }
    }
    if (isCalculable) {
        var attackerNature = attacker.args.nature;
        var defenderNature = defender.args.nature;
        var isAttackerNatureValid = attackerNature === undefined ? true : false;
        var isDefenderNatureValid = defenderNature === undefined ? true : false;
        if (!isAttackerNatureValid && calc_1.NATURES[attackerNature] !== undefined) {
            isAttackerNatureValid = true;
        }
        if (!isDefenderNatureValid && calc_1.NATURES[defenderNature] !== undefined) {
            isDefenderNatureValid = true;
        }
        if (!isAttackerNatureValid || !isDefenderNatureValid) {
            errorMessage += defenderNature + " or " + attackerNature + " are not valid Natures";
            isCalculable = false;
        }
    }
    if (isCalculable) {
        var abilities = calc_1.ABILITIES[calc_1.ABILITIES.length - 1];
        var attackerAbility = attacker.args.ability;
        var defenderAbility = defender.args.ability;
        var isAttackerAbilityValid = attackerAbility === undefined ? true : false;
        var isDefenderAbilityValid = defenderAbility === undefined ? true : false;
        var i = 0;
        while ((!isAttackerAbilityValid || !isDefenderAbilityValid) && i < abilities.length) {
            if (!isAttackerAbilityValid && abilities[i] === attackerAbility) {
                isAttackerAbilityValid = true;
            }
            if (!isDefenderAbilityValid && abilities[i] === defenderAbility) {
                isDefenderAbilityValid = true;
            }
            i++;
        }
        if (!isAttackerAbilityValid || !isDefenderAbilityValid) {
            isCalculable = false;
            errorMessage += attackerAbility + " or " + defenderAbility + " are not valid Abilities";
        }
    }
    if (isCalculable) {
        if (move !== undefined) {
            var moves = calc_1.MOVES[calc_1.MOVES.length - 1];
            if (moves[move] === undefined) {
                errorMessage += move + " is not a valid Move";
                isCalculable = false;
            }
        }
        else {
            errorMessage += "The move passed in input is 'undefined'";
            isCalculable = false;
        }
    }
    return [isCalculable, errorMessage];
}
//# sourceMappingURL=requester.js.map