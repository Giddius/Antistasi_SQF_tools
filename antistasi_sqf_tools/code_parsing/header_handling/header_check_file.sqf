/*

    Author:
        Håkon

    Description:
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna.
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        Excepteur sint occaecat: cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

    extra:
        this is something

*/

private ["_markerX","_damage","_lamps","_onoff","_positionX","_radiusX","_size"];

_markerX = _this select 0;
_onoff = _this select 1;

_positionX = getMarkerPos _markerX;
_damage = 0;
if (not _onoff) then {_damage = 0.95;};

_radiusX = markerSize _markerX;
_size = _radiusX select 0;

for "_i" from 0 to ((count lamptypes) -1) do
    {
    _lamps = _positionX nearObjects [lamptypes select _i,_size];
    {sleep 0.3; _x setDamage _damage} forEach _lamps;
    };
    //123