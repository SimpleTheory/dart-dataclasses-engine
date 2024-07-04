/// AGG ROOT
@Dataclass()
class App {
  Settings settings;
  Map<String, Diet> diets;
  Map<String, Meal> meals;
  Map<String, Ingredient> baseIngredients;

  List<MealComponentFactory> get ingredients => [
        ...baseIngredients.values,
        ...meals.values.where((element) => element.isSubRecipe)
      ];

  void addMeal(Meal meal, {bool save = true}) {
    meals[meal.name] = meal;
    // saveMeal(meal);
    // Saver().app(this);
    if (save) {
      saveEvent([meal]);
    }
  }

  void addBaseIngredient(Ingredient ingredient, {bool save = true}) {
    baseIngredients[ingredient.name] = ingredient;
    // saveIngredient(ingredient);
    // Saver().app(this);
    if (save) {
      saveEvent([ingredient]);
    }
  }

  void addDiet(Diet diet, {bool save = true}) {
    diets[diet.name] = diet;
    // saveDietWithIsolate(diet);
    // Saver().app(this);
    if (save) {
      saveEvent([diet]);
    }
  }

  void updateBaseIngredient(Ingredient ingToUpdate, Ingredient replacer) {
    deleteBaseIngredient(ingToUpdate);
    addBaseIngredient(replacer);
  }

  void updateMeal(Meal mealToUpdate, Meal replacer) {
    deleteMeal(mealToUpdate);
    addMeal(replacer);
  }

  void deleteMeal(Meal meal, {bool save = true}) {
    meals.remove(meal.name);
    if (save) {
      saveEvent([meal]);
    }
    // deleteMealFromSave(meal);
  }

  void deleteBaseIngredient(Ingredient ingredient, {bool save = true}) {
    baseIngredients.remove(ingredient.name);
    if (save) {
      saveEvent([ingredient]);
    }
    // deleteIngredientFromSave(ingredient);
  }

  void deleteDiet(Diet diet, {bool save = true}) {
    diets.remove(diet.name);
    if (save) {
      saveEvent([diet]);
    }
    // deleteDietFromSave(diet);
  }

  void renameDiet(Diet diet, String newName) {
    deleteDiet(diet);
    diet.name = newName;
    addDiet(diet);
  }

  void reorderDiet(int oldIndex, int newIndex, {bool save = true}) {
    diets = reorderMap(diets, oldIndex, newIndex);
    if (save) {
      saveEvent([oldIndex, newIndex]);
    }
  }

  void updateSettings(Settings settings, {bool save = true}) {
    this.settings = settings.copyWithSettings(anthroMetrics: settings.anthroMetrics.copyWithAnthroMetrics());
    if (save) {
      saveEvent([settings]);
    }
  }

  factory App.newApp(Settings settings) =>
      App(settings: settings, diets: {}, meals: {}, baseIngredients: {});

  Day dayFromId(int id){
    for (Diet diet in diets.values){
      for (Day day in diet.days){
        if (day.id == id){
          return day;
        }
      }
    }
    throw ArgumentError('Day does not exist with id: $id');
  }

  void sortIngredientsAndMeals(){
    baseIngredients = baseIngredients.sort((entry) => entry.key.toLowerCase());
    meals = meals.sort((entry) => entry.key.toLowerCase());
  }

  App.dummy() :
      settings = Settings.dummy(),
      diets = {},
      meals = {},
      baseIngredients = {};
  App.dummy2<X>() :
      settings = Settings.dummy(),
      diets = {},
      meals = {},
      baseIngredients = {};

  App.uwu();

  // <editor-fold desc="Dataclass Section">

  // <editor-fold desc="Singleton Pattern">
  // static late final App _singleton;
  //
  // factory App() {
  //   return _singleton;
  // }
  //
  // App._internal({
  //   required this.settings,
  //   required this.diets,
  //   required this.meals,
  //   required this.baseIngredients,
  // });
  //
  // factory App.restart({required Settings settings}) {
  //   _singleton = App._internal(
  //       settings: settings,
  //       diets: <Diet>[],
  //       meals: <Meal>[],
  //       baseIngredients: <Ingredient>[]);
  //   return _singleton;
  // }

  // </editor-fold>

  // <editor-fold desc="Custom Data Functions">
  // App update(
  //     {Settings? settings,
  //     List<Diet>? diets,
  //     List<Meal>? meals,
  //     List<Ingredient>? baseIngredients}) {
  //   _singleton = App._internal(
  //       settings: settings ?? this.settings,
  //       diets: diets ?? this.diets,
  //       meals: meals ?? this.meals,
  //       baseIngredients: baseIngredients ?? this.baseIngredients);
  //   return _singleton;
  // }
  //
  // factory App.fromMap(Map map) {
  //   Settings settings = dejsonify(map['settings']);
  //   List dietsTemp = dejsonify(map['diets']);
  //   List mealsTemp = dejsonify(map['meals']);
  //   List baseIngredientsTemp = dejsonify(map['baseIngredients']);
  //
  //   List<Diet> diets = List<Diet>.from(dietsTemp);
  //
  //   List<Meal> meals = List<Meal>.from(mealsTemp);
  //
  //   List<Ingredient> baseIngredients =
  //       List<Ingredient>.from(baseIngredientsTemp);
  //
  //   _singleton = App._internal(
  //       settings: settings,
  //       diets: diets,
  //       meals: meals,
  //       baseIngredients: baseIngredients);
  //   return _singleton;
  // }
  // factory App.fromJson(String json) => App.fromMap(jsonDecode(json));
  // </editor-fold>

  // <editor-fold desc="Regular Dataclass Section">
  @Generate()
  // <Dataclass>

  App({
    required this.settings,
    required this.diets,
    required this.meals,
    required this.baseIngredients,
  });

  factory App.staticConstructor({
    required settings,
    required diets,
    required meals,
    required baseIngredients,
  }) =>
      App(
          settings: settings,
          diets: diets,
          meals: meals,
          baseIngredients: baseIngredients);

  Map<String, dynamic> get attributes__ => {
        "settings": settings,
        "diets": diets,
        "meals": meals,
        "baseIngredients": baseIngredients
      };

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is App &&
          runtimeType == other.runtimeType &&
          equals(settings, other.settings) &&
          equals(diets, other.diets) &&
          equals(meals, other.meals) &&
          equals(baseIngredients, other.baseIngredients));

  @override
  int get hashCode =>
      settings.hashCode ^
      diets.hashCode ^
      meals.hashCode ^
      baseIngredients.hashCode;

  @override
  String toString() =>
      'App(settings: $settings, diets: $diets, meals: $meals, baseIngredients: $baseIngredients)';

  App copyWithApp(
          {Settings? settings,
          Map<String, Diet>? diets,
          Map<String, Meal>? meals,
          Map<String, Ingredient>? baseIngredients}) =>
      App(
          settings: settings ?? this.settings,
          diets: diets ?? this.diets,
          meals: meals ?? this.meals,
          baseIngredients: baseIngredients ?? this.baseIngredients);

  String toJson() => jsonEncode(toMap());
  Map<String, dynamic> toMap() =>
      {'__type': 'App', ...nestedJsonMap(attributes__)};

  factory App.fromJson(String json) => App.fromMap(jsonDecode(json));

  factory App.fromMap(Map map) {
    Settings settings = dejsonify(map['settings']);
    Map dietsTemp = dejsonify(map['diets']);
    Map mealsTemp = dejsonify(map['meals']);
    Map baseIngredientsTemp = dejsonify(map['baseIngredients']);

    Map<String, Diet> diets = Map<String, Diet>.from(
        dietsTemp.map((__k0, __v0) => MapEntry(__k0 as String, __v0 as Diet)));

    Map<String, Meal> meals = Map<String, Meal>.from(
        mealsTemp.map((__k0, __v0) => MapEntry(__k0 as String, __v0 as Meal)));

    Map<String, Ingredient> baseIngredients = Map<String, Ingredient>.from(
        baseIngredientsTemp
            .map((__k0, __v0) => MapEntry(__k0 as String, __v0 as Ingredient)));

    return App(
        settings: settings,
        diets: diets,
        meals: meals,
        baseIngredients: baseIngredients);
  }
  // </Dataclass>
  // </editor-fold>

  // </editor-fold>
}