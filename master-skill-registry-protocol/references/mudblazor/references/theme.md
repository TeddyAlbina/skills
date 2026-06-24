# Theming Mastery

## 1. Theme Provider – The Root of All Theming

From `https://mudblazor.com/customization/overview#theme-provider`

The `<MudThemeProvider>` must wrap **your entire app** exactly once.

**Recommended placement:** `MainLayout.razor` or `App.razor`

```razor
<MudThemeProvider Theme="@_customTheme" IsDarkMode="@_isDarkMode" Elevation="2">
    <MudDialogProvider />
    <MudSnackbarProvider />
    <MudPopoverProvider />
    <MudResizeListener />

    @Body
</MudThemeProvider>
```

**Key parameters:**
- `Theme` → `MudTheme` instance (null = default theme).
- `IsDarkMode` → `bool` (bindable for runtime toggle).
- `Elevation` → global shadow level override.
- Supports **nested** `MudThemeProvider` for section-specific themes (inheritance works).

**Runtime dark mode toggle example:**
```csharp
@code {
    private bool _isDarkMode = false;
    private MudTheme _customTheme = new();

    private void ToggleDarkMode()
    {
        _isDarkMode = !_isDarkMode;
        StateHasChanged();
    }
}
```

---

## 2. MudTheme Class – Complete Customization Hub

From `https://mudblazor.com/customization/default-theme#mudtheme`

`MudTheme` is the single source of truth. It contains 6 main sections:

```csharp
public class MudTheme
{
    public PaletteLight PaletteLight { get; set; } = new();
    public PaletteDark PaletteDark { get; set; } = new();
    public Typography Typography { get; set; } = new();
    public Shadow Shadows { get; set; } = new();
    public ZIndex ZIndex { get; set; } = new();
    public LayoutProperties LayoutProperties { get; set; } = new();
    public string? PseudoCss { get; set; } // advanced
}
```

**Full production-ready custom theme (copy-paste ready):**

```csharp
private MudTheme _customTheme = new MudTheme()
{
    PaletteLight = new PaletteLight()
    {
        Primary = Colors.DeepPurple.Default,
        Secondary = Colors.Teal.Default,
        Background = Colors.Grey.Lighten5,
        Surface = Colors.Shades.White,
        DrawerBackground = Colors.Shades.White,
        AppbarBackground = Colors.DeepPurple.Default,
        TextPrimary = Colors.Grey.Darken3,
        TextSecondary = Colors.Grey.Darken2,
        ActionDefault = Colors.DeepPurple.Default,
        Success = Colors.Green.Default,
        Error = Colors.Red.Default,
        Warning = Colors.Amber.Default,
        Info = Colors.Blue.Default,
        // ... every property listed in the Palette section below
    },

    PaletteDark = new PaletteDark() { /* mirror structure with dark values */ },

    Typography = new Typography() { /* see section 5 */ },

    LayoutProperties = new LayoutProperties()
    {
        DefaultBorderRadius = "12px",
        DrawerWidthLeft = "280px",
        DrawerWidthRight = "320px",
        DrawerMiniWidthLeft = "72px",
        AppbarHeight = "68px",
        AppbarMinHeight = "56px"
    },

    ZIndex = new ZIndex()
    {
        Drawer = 1200,
        AppBar = 1300,
        Popover = 1400,
        Dialog = 1500,
        Snackbar = 1600,
        Tooltip = 1700,
        Menu = 1800
    }
};
```

---

## 3. Palette – Every Color Property (from official docs)

| Property                          | Type       | Default Light Value                          | Default Dark Value                          | CSS Variable                                      | Usage / Notes |
|-----------------------------------|------------|----------------------------------------------|---------------------------------------------|---------------------------------------------------|---------------|
| **Black**                         | MudColor   | rgba(39,44,52,1)                             | rgba(39,39,47,1)                            | `--mud-palette-black`                            | Pure black |
| **White**                         | MudColor   | rgba(255,255,255,1)                          | rgba(255,255,255,1)                         | `--mud-palette-white`                            | Pure white |
| **Primary**                       | MudColor   | rgba(89,74,226,1)                            | rgba(119,107,231,1)                         | `--mud-palette-primary`                          | Main brand color |
| **PrimaryContrastText**           | MudColor   | rgba(255,255,255,1)                          | rgba(255,255,255,1)                         | `--mud-palette-primary-text`                     | Text on Primary |
| **Secondary**                     | MudColor   | rgba(255,64,129,1)                           | rgba(255,64,129,1)                          | `--mud-palette-secondary`                        | Accent color |
| **SecondaryContrastText**         | MudColor   | rgba(255,255,255,1)                          | rgba(255,255,255,1)                         | `--mud-palette-secondary-text`                   | Text on Secondary |
| **Tertiary**                      | MudColor   | rgba(30,200,165,1)                           | rgba(30,200,165,1)                          | `--mud-palette-tertiary`                         | Extra accent |
| **TertiaryContrastText**          | MudColor   | rgba(255,255,255,1)                          | rgba(255,255,255,1)                         | `--mud-palette-tertiary-text`                    | Text on Tertiary |
| **Info**                          | MudColor   | rgba(33,150,243,1)                           | rgba(50,153,255,1)                          | `--mud-palette-info`                             | Informational |
| **InfoContrastText**              | MudColor   | rgba(255,255,255,1)                          | rgba(255,255,255,1)                         | `--mud-palette-info-text`                        | Text on Info |
| **Success**                       | MudColor   | rgba(0,200,83,1)                             | rgba(11,186,131,1)                          | `--mud-palette-success`                          | Success messages |
| **SuccessContrastText**           | MudColor   | rgba(255,255,255,1)                          | rgba(255,255,255,1)                         | `--mud-palette-success-text`                     | Text on Success |
| **Warning**                       | MudColor   | rgba(255,152,0,1)                            | rgba(255,168,0,1)                           | `--mud-palette-warning`                          | Warnings |
| **WarningContrastText**           | MudColor   | rgba(255,255,255,1)                          | rgba(255,255,255,1)                         | `--mud-palette-warning-text`                     | Text on Warning |
| **Error**                         | MudColor   | rgba(244,67,54,1)                            | rgba(246,78,98,1)                           | `--mud-palette-error`                            | Errors |
| **ErrorContrastText**             | MudColor   | rgba(255,255,255,1)                          | rgba(255,255,255,1)                         | `--mud-palette-error-text`                       | Text on Error |
| **Dark**                          | MudColor   | rgba(66,66,66,1)                             | rgba(39,39,47,1)                            | `--mud-palette-dark`                             | Dark theme base |
| **DarkContrastText**              | MudColor   | rgba(255,255,255,1)                          | rgba(255,255,255,1)                         | `--mud-palette-dark-text`                        | Text on Dark |
| **TextPrimary**                   | MudColor   | rgba(66,66,66,1)                             | rgba(255,255,255,0.70)                      | `--mud-palette-text-primary`                     | Main body text |
| **TextSecondary**                 | MudColor   | rgba(0,0,0,0.54)                             | rgba(255,255,255,0.50)                      | `--mud-palette-text-secondary`                   | Secondary text |
| **TextDisabled**                  | MudColor   | rgba(0,0,0,0.38)                             | rgba(255,255,255,0.20)                      | `--mud-palette-text-disabled`                    | Disabled text |
| **ActionDefault**                 | MudColor   | rgba(0,0,0,0.54)                             | rgba(173,173,177,1)                         | `--mud-palette-action-default`                   | Default icons/buttons |
| **ActionDisabled**                | MudColor   | rgba(0,0,0,0.26)                             | rgba(255,255,255,0.26)                      | `--mud-palette-action-disabled`                  | Disabled actions |
| **ActionDisabledBackground**      | MudColor   | rgba(0,0,0,0.12)                             | rgba(255,255,255,0.12)                      | `--mud-palette-action-disabled-background`       | Disabled bg |
| **Background**                    | MudColor   | rgba(255,255,255,1)                          | rgba(50,51,61,1)                            | `--mud-palette-background`                       | Page background |
| **BackgroundGray**                | MudColor   | rgba(245,245,245,1)                          | rgba(39,39,47,1)                            | `--mud-palette-background-gray`                  | Gray background |
| **Surface**                       | MudColor   | rgba(255,255,255,1)                          | rgba(55,55,64,1)                            | `--mud-palette-surface`                          | Cards, dialogs, paper |
| **DrawerBackground**              | MudColor   | rgba(255,255,255,1)                          | rgba(39,39,47,1)                            | `--mud-palette-drawer-background`                | Left/right drawer |
| **DrawerText**                    | MudColor   | rgba(66,66,66,1)                             | rgba(255,255,255,0.50)                      | `--mud-palette-drawer-text`                      | Drawer text |
| **DrawerIcon**                    | MudColor   | rgba(97,97,97,1)                             | rgba(255,255,255,0.50)                      | `--mud-palette-drawer-icon`                      | Drawer icons |
| **AppbarBackground**              | MudColor   | rgba(89,74,226,1)                            | rgba(39,39,47,1)                            | `--mud-palette-appbar-background`                | Top app bar |
| **AppbarText**                    | MudColor   | rgba(255,255,255,1)                          | rgba(255,255,255,0.70)                      | `--mud-palette-appbar-text`                      | App bar text |
| **LinesDefault**                  | MudColor   | rgba(0,0,0,0.12)                             | rgba(255,255,255,0.12)                      | `--mud-palette-lines-default`                    | General borders |
| **LinesInputs**                   | MudColor   | rgba(189,189,189,1)                          | rgba(255,255,255,0.30)                      | `--mud-palette-lines-inputs`                     | Input borders |
| **TableLines**                    | MudColor   | rgba(224,224,224,1)                          | rgba(255,255,255,0.12)                      | `--mud-palette-table-lines`                      | DataGrid borders |
| **TableStriped**                  | MudColor   | rgba(0,0,0,0.02)                             | rgba(255,255,255,0.20)                      | `--mud-palette-table-striped`                    | Striped rows |
| **TableHover**                    | MudColor   | rgba(0,0,0,0.04)                             | rgba(255,255,255,0.08)                      | `--mud-palette-table-hover`                      | Hover rows |
| **Divider**                       | MudColor   | rgba(224,224,224,1)                          | rgba(255,255,255,0.12)                      | `--mud-palette-divider`                          | Horizontal dividers |
| **DividerLight**                  | MudColor   | rgba(0,0,0,0.8)                              | rgba(255,255,255,0.06)                      | `--mud-palette-divider-light`                    | Light dividers |
| **Skeleton**                      | MudColor   | rgba(0,0,0,0.11)                             | rgba(255,255,255,0.11)                      | `--mud-palette-skeleton`                         | Loading skeletons |

### Important Official Documentation Notes

- **PaletteLight** and **PaletteDark** are used together in one `MudTheme`.  
- MudBlazor automatically generates **CSS variables** for every property (see column above).  
- Every semantic color also generates **Lighten** / **Darken** variants automatically:  
  `PrimaryLighten`, `PrimaryDarken`, `PrimaryLighten1` … `PrimaryDarken3`, etc.  
  (These are available as strings in CSS and in the `MudColor` class).
- You **must** override **both** `PaletteLight` **and** `PaletteDark` if you want perfect dark-mode support.
- Use the `MudColor` class for advanced manipulation:
  ```csharp
  var myColor = new MudColor(89, 74, 226);   // RGB
  var lighter = myColor.Lighten(0.3);
  var withAlpha = myColor.SetAlpha(0.7);

 
**Advanced color handling:**
- Use `MudColor` class for dynamic manipulation: `new MudColor(89, 74, 226)`.
- Helpers: `Color = MudColor.FromString("#594AE2")`.
- Darken/Lighten variants are auto-generated as CSS strings (`--mud-palette-primary-darken`).

**Best practice:** Always define both `PaletteLight` and `PaletteDark` for seamless dark mode.

---

## 4. Typography – How It Works

From `https://mudblazor.com/customization/typography#how-it-works`

`Typography` object controls **every** text style via `MudText` component (`Typo` enum).

```csharp
Typography = new Typography()
{
    Default = new BaseTypography
    {
        FontFamily = ["Inter", "Roboto", "sans-serif"],
        FontSize = "1rem",
        FontWeight = 400,
        LineHeight = 1.5,
        LetterSpacing = "0.00938em"
    },
    H1 = new BaseTypography { FontSize = "6rem", FontWeight = 300, LineHeight = 1.167 },
    H2 = new BaseTypography { FontSize = "3.75rem", FontWeight = 300 },
    H3 = new BaseTypography { FontSize = "3rem", FontWeight = 400 },
    H4 = new BaseTypography { FontSize = "2.125rem", FontWeight = 400 },
    H5 = new BaseTypography { FontSize = "1.5rem", FontWeight = 400 },
    H6 = new BaseTypography { FontSize = "1.25rem", FontWeight = 500 },
    Subtitle1 = new BaseTypography { FontSize = "1rem" },
    Subtitle2 = new BaseTypography { FontSize = "0.875rem" },
    Body1 = new BaseTypography { FontSize = "1rem" },
    Body2 = new BaseTypography { FontSize = "0.875rem" },
    Button = new BaseTypography { TextTransform = "uppercase", FontWeight = 500 },
    Caption = new BaseTypography { FontSize = "0.75rem" },
    Overline = new BaseTypography { FontSize = "0.75rem", TextTransform = "uppercase" }
};
```

**Usage in components:**
```razor
<MudText Typo="Typo.h1" Color="Color.Primary" GutterBottom="true">Title</MudText>
```

CSS variables generated: `--mud-typography-h1-size`, `--mud-typography-button-weight`, etc.

---

## 5. Z-Index – Layer Management

From `https://mudblazor.com/customization/z-index#mudblazor-z-index's`

`ZIndex` class controls stacking order for overlays:

```csharp
ZIndex = new ZIndex()
{
    Drawer = 1200,
    AppBar = 1300,
    Popover = 1400,
    Dialog = 1500,
    Snackbar = 1600,
    Tooltip = 1700,
    Menu = 1800
};
```

**Common conflicts & fixes:**
- Dialog inside Drawer → increase `ZIndex.Dialog` or use `MaxZIndex`.
- Custom popovers → use `Style="z-index: 9999;"` or override CSS variable `--mud-zindex-popover`.

---

## 6. Pseudo CSS – Global & Scoped Overrides

From `https://mudblazor.com/customization/pseudocss#mudblazor-pseudo-css`

MudBlazor exposes **hundreds of CSS variables** (`--mud-*`).

**Global override (wwwroot/css/app.css):**
```css
:root {
    --mud-palette-primary: #594AE2;
    --mud-typography-h1-size: 5rem;
    --mud-button-border-radius: 9999px;
}
```

**Component-scoped (inside .razor):**
```razor
<MudButton Class="my-special-btn">Click</MudButton>

<style>
    .my-special-btn {
        --mud-button-font-weight: 700;
    }
    .my-special-btn::after {
        content: " ✨";
    }
</style>
```

**Pro tip:** Use `:root`, `.mud-xxx`, or descendant selectors. All components support `Class` + `Style` parameters.

---

## 7. LayoutProperties & Shadows

- `DefaultBorderRadius`, `DrawerWidth*`, `AppbarHeight`, etc.
- `Shadows` array controls all `Elevation` levels (0-24).

---

## 8. Advanced Agent Skills

### Runtime Theme Switching
```csharp
private MudTheme _theme1 = new MudTheme { /* corporate */ };
private MudTheme _theme2 = new MudTheme { /* neon */ };

<MudThemeProvider Theme="@_currentTheme">
```

### Nested Themes
Wrap a section in its own `MudThemeProvider` for dashboards, admin panels, etc.

### MudColor Advanced Usage
```csharp
var myColor = new MudColor(0x59, 0x4A, 0xE2);
var lighter = myColor.Lighten(0.2);
```

### Performance & Best Practices
- Use `MudServicesConfiguration` for global defaults.
- Prefer `MudBlazor` icons over external libraries.
- Always wrap forms with `<MudForm>`.
- For large tables → `MudDataGrid` with virtualization.
- Accessibility: Every component ships with full ARIA + keyboard navigation.

### Common Pitfalls
- Forgetting `AddMudServices()` → blank UI.
- Missing `MudThemeProvider` → default theme only.
- Hard-coding colors instead of using theme → breaks dark mode.
- Z-index wars → always use the `ZIndex` class first.

---

## 10. Quick-Start Component Recipes (Agent Ready-to-Use)

**Themed AppBar + Drawer:**
```razor
<MudAppBar Elevation="1">...</MudAppBar>
<MudDrawer Open="true" Elevation="2">...</MudDrawer>
```

**Dark Mode Toggle Button:**
```razor
<MudSwitch @bind-Value="@_isDarkMode" Color="Color.Primary" />
```


**Documentation**
- https://mudblazor.com/docs/overview
- https://mudblazor.com/customization/default-theme#mudtheme
- https://mudblazor.com/customization/overview#theme-provider
- https://mudblazor.com/customization/palette
- https://mudblazor.com/customization/pseudocss#mudblazor-pseudo-css
- https://mudblazor.com/customization/typography#how-it-works
- https://mudblazor.com/customization/z-index#mudblazor-z-index's