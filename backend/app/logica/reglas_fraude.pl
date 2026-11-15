% ============================================================================
% FinGuard - Motor de Inferencia Antifraude y Auditoria Explicable (Unidad 2)
% Base de conocimiento dinamica + reglas de unificacion, resolucion y backtracking
% ============================================================================

:- dynamic transaccion/7.
% transaccion(Id, Fecha, Hora, Comercio, Ciudad, Canal, MontoPEN).

:- dynamic perfil_usuario/3.
% perfil_usuario(CiudadHabitual, Modo, UmbralZ).

:- dynamic z_score_tx/2.
% z_score_tx(Id, ZScore).

% Limpieza segura de hechos antes de cada nueva auditoria
limpiar_hechos :-
    retractall(transaccion(_, _, _, _, _, _, _)),
    retractall(perfil_usuario(_, _, _)),
    retractall(z_score_tx(_, _)).

% Conversion auxiliar de hora 'HH:MM' a minutos desde medianoche
hora_a_minutos(HoraAtom, Minutos) :-
    atom_string(HoraAtom, HoraStr),
    split_string(HoraStr, ":", "", [HStr, MStr]),
    number_string(H, HStr),
    number_string(M, MStr),
    Minutos is H * 60 + M.

% Predicado horario de madrugada (00:00 a 05:59)
hora_madrugada(HoraAtom) :-
    hora_a_minutos(HoraAtom, Minutos),
    Minutos >= 0,
    Minutos =< 359.

% Normalizacion insensible a mayusculas para comparacion de ciudades
ciudades_distintas(C1, C2) :-
    downcase_atom(C1, L1),
    downcase_atom(C2, L2),
    L1 \= L2.

% Umbral nocturno dinamico segun modo del usuario
umbral_nocturno(ahorro_estricto, 100.0).
umbral_nocturno(normal, 200.0).

% ============================================================================
% REGLA 1: Viaje imposible entre ciudades distintas (Posible clonacion fisica)
% Dos compras presenciales el mismo dia en ciudades distintas con < 180 min
% ============================================================================
viaje_imposible(Id1, Id2, Fecha, Hora1, Hora2, C1, C2, DiffMin) :-
    transaccion(Id1, Fecha, Hora1, _, C1, presencial, _),
    transaccion(Id2, Fecha, Hora2, _, C2, presencial, _),
    Id1 \= Id2,
    ciudades_distintas(C1, C2),
    hora_a_minutos(Hora1, Min1),
    hora_a_minutos(Hora2, Min2),
    Min1 =< Min2,
    DiffMin is Min2 - Min1,
    DiffMin < 180,
    (Min1 < Min2 ; Id1 @< Id2).

% ============================================================================
% REGLA 2: Compra online nocturna atipica (Madrugada con monto elevado)
% ============================================================================
compra_nocturna_atipica(Id, Fecha, Hora, Comercio, Ciudad, Monto) :-
    perfil_usuario(_, Modo, _),
    umbral_nocturno(Modo, Umbral),
    transaccion(Id, Fecha, Hora, Comercio, Ciudad, online, Monto),
    hora_madrugada(Hora),
    Monto >= Umbral.

% ============================================================================
% REGLA 3: Cobro duplicado en el mismo comercio (diferencia <= 30 minutos)
% ============================================================================
cobro_duplicado_regla(Id1, Id2, Fecha, Comercio, Monto, DiffMin) :-
    transaccion(Id1, Fecha, Hora1, Comercio, _, _, Monto1),
    transaccion(Id2, Fecha, Hora2, Comercio, _, _, Monto2),
    Id1 @< Id2,
    abs(Monto1 - Monto2) < 0.01,
    Monto is Monto1,
    hora_a_minutos(Hora1, M1),
    hora_a_minutos(Hora2, M2),
    DiffMin is abs(M2 - M1),
    DiffMin =< 30.

% ============================================================================
% REGLA 4: Monto anomalo segun perfil estadistico (Z-Score)
% ============================================================================
monto_anomalo_zscore(Id, Comercio, Monto, Z, UmbralZ) :-
    perfil_usuario(_, _, UmbralZ),
    z_score_tx(Id, Z),
    Z >= UmbralZ,
    transaccion(Id, _, _, Comercio, _, _, Monto).

% ============================================================================
% REGLA 5: Compra presencial fuera de la ciudad habitual
% (Solo se emite si no fue ya capturada por viaje_imposible para evitar ruido)
% ============================================================================
presencial_fuera_ciudad(Id, Ciudad, CiudadHabitual, Monto) :-
    perfil_usuario(CiudadHabitual, _, _),
    transaccion(Id, _, _, _, Ciudad, presencial, Monto),
    ciudades_distintas(Ciudad, CiudadHabitual),
    \+ viaje_imposible(_, Id, _, _, _, _, _, _),
    \+ viaje_imposible(Id, _, _, _, _, _, _, _),
    Monto >= 80.0.

% ============================================================================
% PREDICADO UNIFICADO DE EXPLICABILIDAD Y TRAZA PARA LA API
% ============================================================================

alerta_detectada(Id2, 'viaje_imposible/8', critica,
    'Posible clonacion de tarjeta (Viaje imposible)',
    Explicacion, Traza) :-
    viaje_imposible(Id1, Id2, Fecha, Hora1, Hora2, C1, C2, DiffMin),
    transaccion(Id1, Fecha, Hora1, Com1, C1, presencial, M1),
    transaccion(Id2, Fecha, Hora2, Com2, C2, presencial, M2),
    format(atom(Explicacion),
        'Posible clonacion: compra presencial en ~w a las ~w (~w, S/ ~2f) y otra en ~w a las ~w (~w, S/ ~2f) el ~w, con solo ~w minutos de diferencia.',
        [C1, Hora1, Id1, M1, C2, Hora2, Id2, M2, Fecha, DiffMin]),
    format(atom(T1), 'transaccion(~w, ~w, ~w, ~w, ~w, presencial, ~2f)', [Id1, Fecha, Hora1, Com1, C1, M1]),
    format(atom(T2), 'transaccion(~w, ~w, ~w, ~w, ~w, presencial, ~2f)', [Id2, Fecha, Hora2, Com2, C2, M2]),
    format(atom(T3), 'ciudades_distintas(~w, ~w) -> true', [C1, C2]),
    format(atom(T4), 'diferencia_minutos(~w, ~w, ~w) -> ~w < 180 min', [Hora1, Hora2, DiffMin, DiffMin]),
    format(atom(T5), 'regla_activada: viaje_imposible(~w, ~w, ~w, ~w, ~w min)', [Id1, Id2, C1, C2, DiffMin]),
    Traza = [T1, T2, T3, T4, T5].

alerta_detectada(Id, 'compra_nocturna_atipica/6', critica,
    'Compra online nocturna atipica',
    Explicacion, Traza) :-
    compra_nocturna_atipica(Id, Fecha, Hora, Comercio, Ciudad, Monto),
    perfil_usuario(_, Modo, _),
    umbral_nocturno(Modo, Umbral),
    format(atom(Explicacion),
        'Compra online atipica de S/ ~2f a las ~w AM en ~w (~w) el ~w, superando el umbral nocturno de S/ ~2f.',
        [Monto, Hora, Comercio, Ciudad, Fecha, Umbral]),
    format(atom(T1), 'transaccion(~w, ~w, ~w, ~w, ~w, online, ~2f)', [Id, Fecha, Hora, Comercio, Ciudad, Monto]),
    format(atom(T2), 'hora_madrugada(~w) -> true (00:00 - 05:59)', [Hora]),
    format(atom(T3), 'umbral_nocturno(~w, ~2f) -> ~2f >= ~2f', [Modo, Umbral, Monto, Umbral]),
    format(atom(T4), 'regla_activada: compra_nocturna_atipica(~w, ~w, ~2f)', [Id, Hora, Monto]),
    Traza = [T1, T2, T3, T4].

alerta_detectada(Id2, 'cobro_duplicado_regla/6', alta,
    'Posible cobro duplicado en comercio',
    Explicacion, Traza) :-
    cobro_duplicado_regla(Id1, Id2, Fecha, Comercio, Monto, DiffMin),
    transaccion(Id1, Fecha, H1, Comercio, _, _, _),
    transaccion(Id2, Fecha, H2, Comercio, _, _, _),
    format(atom(Explicacion),
        'Se detectaron dos cargos identicos de S/ ~2f en ~w el ~w (~w a las ~w y ~w a las ~w) separados por ~w minutos.',
        [Monto, Comercio, Fecha, Id1, H1, Id2, H2, DiffMin]),
    format(atom(T1), 'transaccion(~w, ~w, ~w, ~w, ..., ~2f)', [Id1, Fecha, H1, Comercio, Monto]),
    format(atom(T2), 'transaccion(~w, ~w, ~w, ~w, ..., ~2f)', [Id2, Fecha, H2, Comercio, Monto]),
    format(atom(T3), 'diferencia_minutos(~w, ~w, ~w) -> ~w =< 30 min', [H1, H2, DiffMin, DiffMin]),
    format(atom(T4), 'regla_activada: cobro_duplicado_regla(~w, ~w, ~w, ~2f)', [Id1, Id2, Comercio, Monto]),
    Traza = [T1, T2, T3, T4].

alerta_detectada(Id, 'monto_anomalo_zscore/5', alta,
    'Monto estadisticamente anomalo fuera de perfil',
    Explicacion, Traza) :-
    monto_anomalo_zscore(Id, Comercio, Monto, Z, UmbralZ),
    \+ compra_nocturna_atipica(Id, _, _, _, _, _),
    format(atom(Explicacion),
        'Gasto de S/ ~2f en ~w es mucho mas alto que tu consumo habitual (indicador ~2f vs limite ~2f).',
        [Monto, Comercio, Z, UmbralZ]),
    format(atom(T1), 'z_score_tx(~w, ~2f)', [Id, Z]),
    format(atom(T2), 'perfil_usuario(..., UmbralZ=~2f) -> ~2f >= ~2f', [UmbralZ, Z, UmbralZ]),
    format(atom(T3), 'regla_activada: monto_anomalo_zscore(~w, ~w, ~2f)', [Id, Comercio, Monto]),
    Traza = [T1, T2, T3].

alerta_detectada(Id, 'presencial_fuera_ciudad/4', media,
    'Compra presencial fuera de tu ciudad habitual',
    Explicacion, Traza) :-
    presencial_fuera_ciudad(Id, Ciudad, CiudadHabitual, Monto),
    transaccion(Id, Fecha, Hora, Comercio, Ciudad, presencial, Monto),
    format(atom(Explicacion),
        'Compra presencial de S/ ~2f en ~w (~w a las ~w) fuera de tu ciudad habitual registrada (~w).',
        [Monto, Comercio, Ciudad, Hora, CiudadHabitual]),
    format(atom(T1), 'perfil_usuario(~w, ...)', [CiudadHabitual]),
    format(atom(T2), 'transaccion(~w, ~w, ~w, ~w, ~w, presencial, ~2f)', [Id, Fecha, Hora, Comercio, Ciudad, Monto]),
    format(atom(T3), 'ciudades_distintas(~w, ~w) -> true', [Ciudad, CiudadHabitual]),
    format(atom(T4), 'regla_activada: presencial_fuera_ciudad(~w, ~w)', [Id, Ciudad]),
    Traza = [T1, T2, T3, T4].
