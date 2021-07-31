import {calculate, Generations, Pokemon, Move, Field, Result, SPECIES, ITEMS, NATURES, ABILITIES, MOVES} from '@smogon/calc';
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path'

//call the function to calculate
calculateDamage();

function calculateDamage(){
  const fileName:string =  process.argv[2];
  const folderName: string = process.argv[3];
  const destinationFolderName:string = process.argv[4];
  if(fileName !== undefined && folderName !== undefined && destinationFolderName !== undefined){
    var jsonPath = join(__dirname, '..', folderName, fileName);
    var obj = JSON.parse(readFileSync(jsonPath, 'utf8'));

    const attacker = obj.attacker;
    const defender = obj.defender;
    const move = obj.move;
    const field = obj.field;
    const gen = Generations.get(8);

    if(field.terrain !== undefined && field.terrain === "None"){
      field.terrain = undefined
    }

    if(field.weather !== undefined && field.weather === "None"){
      field.weather = undefined
    }

    var validity = isDataValid(move.name, attacker, defender);
    const isCalculable:boolean = validity[0];
    const errorMessage:string = validity[1];
    
    var text_result:string = "";

    try{
      if(isCalculable){
        const result:Result = calculate(
          gen,
          new Pokemon(gen, attacker.name, attacker.args),
          new Pokemon(gen, defender.name, defender.args),
          new Move(gen, move.name, move),
          new Field(field)
        );
        text_result = printValidResult(result);
      } else {
        text_result = errorMessage;
      }
    }catch(error){
      console.log(error);
      text_result = "An unexpected error occurred, if the problem persists please contact @Alghisius"
    }
    var resultPath = join(__dirname, '..', destinationFolderName, fileName);
    writeFileSync(resultPath, text_result);
  } else {
    console.log("wrong number of argument passed");
  }
}

function printValidResult(result:Result):string{
  var rawDesc = result.rawDesc;
  var damage:any = result.damage;
  var defenderHP = result.defender.originalCurHP;

  var text_result:string = result.fullDesc();
  
  if(damage !== undefined && typeof(damage) === 'object'){
    text_result += "\nPossible damage amounts: (";
    for(let i = 0; i < damage.length; i++){
      text_result += damage[i];
      if(i+1 < damage.length){
        text_result += ", ";
      }
    }
    text_result += ")";
  }
  return text_result;
}

function isDataValid(move, attacker, defender):[boolean, string]{
  let isCalculable: boolean = true;
  var errorMessage:string = "ERORR: ";

  if(attacker === undefined || defender === undefined){
    isCalculable = false;
    errorMessage += "One of the Pokémon was 'undefined'";
  }

  if(isCalculable){
    let isAttackerPkmn:boolean = false;
    let isDefenderPkmn:boolean = false;
    let specie = SPECIES[SPECIES.length-1]
    if(specie[attacker.name] !== undefined){
      isAttackerPkmn = true;
    }
    if(specie[defender.name] !== undefined){
      isDefenderPkmn = true;
    }
    if(!isAttackerPkmn || !isDefenderPkmn){
      isCalculable = false;
      errorMessage += defender.name + " or " + attacker.name + " are not Pokémon Species"
    }
  }

  if(isCalculable){
    let items = ITEMS[ITEMS.length-1]
    let attackerItem = attacker.args.item;
    let defenderItem = defender.args.item;
    let isAttackerItemValid:boolean = attackerItem === undefined ? true : false;
    let isDefenderItemValid:boolean = defenderItem === undefined ? true : false;

    let i = 0;
    while((!isAttackerItemValid || !isDefenderItemValid) && i < items.length){
        if(!isAttackerItemValid && items[i] === attackerItem){
          isAttackerItemValid = true;
        }
        if(!isDefenderItemValid && items[i] === defenderItem){
          isDefenderItemValid = true;
        }
        i++;
    }

    if(!isAttackerItemValid || !isDefenderItemValid){
      isCalculable = false;
      errorMessage += attackerItem + " or " + defenderItem + " are not valid Items"
    }
  }

  if(isCalculable){
    let attackerNature = attacker.args.nature;
    let defenderNature = defender.args.nature;
    let isAttackerNatureValid:boolean = attackerNature === undefined ? true : false;
    let isDefenderNatureValid:boolean = defenderNature === undefined ? true : false;
    if(!isAttackerNatureValid && NATURES[attackerNature] !== undefined){
      isAttackerNatureValid = true;
    }
    if(!isDefenderNatureValid && NATURES[defenderNature] !== undefined){
      isDefenderNatureValid = true;
    }
    if(!isAttackerNatureValid || !isDefenderNatureValid){
      errorMessage += defenderNature + " or " + attackerNature + " are not valid Natures";
      isCalculable = false;
    }
  }

  if(isCalculable){
    let abilities = ABILITIES[ABILITIES.length-1]
    let attackerAbility = attacker.args.ability;
    let defenderAbility = defender.args.ability;
    let isAttackerAbilityValid:boolean = attackerAbility === undefined ? true : false;
    let isDefenderAbilityValid:boolean = defenderAbility === undefined ? true : false;

    let i = 0;
    while((!isAttackerAbilityValid || !isDefenderAbilityValid) && i < abilities.length){
        if(!isAttackerAbilityValid && abilities[i] === attackerAbility){
          isAttackerAbilityValid = true;
        }
        if(!isDefenderAbilityValid && abilities[i] === defenderAbility){
          isDefenderAbilityValid = true;
        }
        i++;
    }

    if(!isAttackerAbilityValid || !isDefenderAbilityValid){
      isCalculable = false;
      errorMessage += attackerAbility + " or " + defenderAbility + " are not valid Abilities"
    }
  }

  if(isCalculable){
    if(move !== undefined){
      let moves = MOVES[MOVES.length-1]
      if(moves[move] === undefined){
        errorMessage += move + " is not a valid Move";
        isCalculable = false;
      }
    } else {
      errorMessage += "The move passed in input is 'undefined'";
      isCalculable = false;
    }
  }

  return [isCalculable, errorMessage]
}