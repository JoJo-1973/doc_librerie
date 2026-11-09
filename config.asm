; ==============================================================================
; FILE:           config.asm
; PROGETTO:       Template di Configurazione del Progetto (config.asm)
; TARGET:         ACME Assembler / MOS 6510 (Commodore 64)
; DESCRIZIONE:    Template di configurazione: parametri di configurazione e punti
;                 di personalizzazione delle librerie c64, chip, fp, io, math e system.
; ==============================================================================

; ------------------------------------------------------------------------------
; Libreria fp
; ------------------------------------------------------------------------------

; ----------------------------------------
; fp_error.asm
; ----------------------------------------

__USE_FP_ERROR_HANDLER      = 0     ; Subroutine FP_ERROR_HANDLER (1: da assemblare)

; ------------------------------------------------------------------------------
; Libreria io
; ------------------------------------------------------------------------------

; ----------------------------------------
; disk_tools.asm
; ----------------------------------------

__USE_DISK_STATUS           = 0     ; Subroutine DISK_STATUS (1: da assemblare)
__USE_DECODE_DISK_STATUS    = 0     ; Subroutine DECODE_DISK_STATUS (1: da assemblare)
__USE_DISK_DIRECTORY        = 0     ; Subroutine DISK_DIRECTORY (1: da assemblare; richiede DISK_STATUS)
__USE_DISK_COMMAND          = 0     ; Subroutine DISK_COMMAND (1: da assemblare; richiede DISK_STATUS)

; ----------------------------------------
; keyboard_tools.asm
; ----------------------------------------

__USE_KEYSCAN               = 0     ; Subroutine KEYSCAN (1: da assemblare)

; ------------------------------------------------------------------------------
; Libreria math
; ------------------------------------------------------------------------------

; ----------------------------------------
; math_div.asm
; ----------------------------------------

__USE_DIV_8X8               = 0     ; Subroutine DIV_8X8 (1: da assemblare)
__USE_SDIV_8X8              = 0     ; Subroutine SDIV_8X8 (1: da assemblare)
__USE_DIV_16X8              = 0     ; Subroutine DIV_16X8 (1: da assemblare)
__USE_SDIV_16X8             = 0     ; Subroutine SDIV_16X8 (1: da assemblare)
__USE_DIV_24X8              = 0     ; Subroutine DIV_24X8 (1: da assemblare)
__USE_SDIV_24X8             = 0     ; Subroutine SDIV_24X8 (1: da assemblare)
__USE_DIV_32X8              = 0     ; Subroutine DIV_32X8 (1: da assemblare)
__USE_SDIV_32X8             = 0     ; Subroutine SDIV_32X8 (1: da assemblare)
__USE_DIV_16X16             = 0     ; Subroutine DIV_16X16 (1: da assemblare)
__USE_SDIV_16X16            = 0     ; Subroutine SDIV_16X16 (1: da assemblare)
__USE_DIV_24X16             = 0     ; Subroutine DIV_24X16 (1: da assemblare)
__USE_SDIV_24X16            = 0     ; Subroutine SDIV_24X16 (1: da assemblare)
__USE_DIV_32X16             = 0     ; Subroutine DIV_32X16 (1: da assemblare)
__USE_SDIV_32X16            = 0     ; Subroutine SDIV_32X16 (1: da assemblare)
__USE_DIV_24X24             = 0     ; Subroutine DIV_24X24 (1: da assemblare)
__USE_SDIV_24X24            = 0     ; Subroutine SDIV_24X24 (1: da assemblare)
__USE_DIV_32X24             = 0     ; Subroutine DIV_32X24 (1: da assemblare)
__USE_SDIV_32X24            = 0     ; Subroutine SDIV_32X24 (1: da assemblare)
__USE_DIV_32X32             = 0     ; Subroutine DIV_32X32 (1: da assemblare)
__USE_SDIV_32X32            = 0     ; Subroutine SDIV_32X32 (1: da assemblare)

; ----------------------------------------
; math_mult.asm
; ----------------------------------------

__USE_MUL_8X8               = 0     ; Subroutine MUL_8X8 (1: da assemblare)
__USE_SMUL_8X8              = 0     ; Subroutine SMUL_8X8 (1: da assemblare)
__USE_MUL_16X8              = 0     ; Subroutine MUL_16X8 (1: da assemblare)
__USE_SMUL_16X8             = 0     ; Subroutine SMUL_16X8 (1: da assemblare)
__USE_MUL_24X8              = 0     ; Subroutine MUL_24X8 (1: da assemblare)
__USE_SMUL_24X8             = 0     ; Subroutine SMUL_24X8 (1: da assemblare)
__USE_MUL_32X8              = 0     ; Subroutine MUL_32X8 (1: da assemblare)
__USE_SMUL_32X8             = 0     ; Subroutine SMUL_32X8 (1: da assemblare)
__USE_MUL_16X16             = 0     ; Subroutine MUL_16X16 (1: da assemblare)
__USE_SMUL_16X16            = 0     ; Subroutine SMUL_16X16 (1: da assemblare)
__USE_MUL_24X16             = 0     ; Subroutine MUL_24X16 (1: da assemblare)
__USE_SMUL_24X16            = 0     ; Subroutine SMUL_24X16 (1: da assemblare)
__USE_MUL_32X16             = 0     ; Subroutine MUL_32X16 (1: da assemblare)
__USE_SMUL_32X16            = 0     ; Subroutine SMUL_32X16 (1: da assemblare)
__USE_MUL_24X24             = 0     ; Subroutine MUL_24X24 (1: da assemblare)
__USE_SMUL_24X24            = 0     ; Subroutine SMUL_24X24 (1: da assemblare)
__USE_MUL_32X24             = 0     ; Subroutine MUL_32X24 (1: da assemblare)
__USE_SMUL_32X24            = 0     ; Subroutine SMUL_32X24 (1: da assemblare)
__USE_MUL_32X32             = 0     ; Subroutine MUL_32X32 (1: da assemblare)
__USE_SMUL_32X32            = 0     ; Subroutine SMUL_32X32 (1: da assemblare)

; ------------------------------------------------------------------------------
; Libreria system
; ------------------------------------------------------------------------------

; ----------------------------------------
; basic_tools.asm
; ----------------------------------------

__USE_LOMEM                 = 0     ; Subroutine LOMEM (1: da assemblare)
__USE_HIMEM                 = 0     ; Subroutine HIMEM (1: da assemblare)

; ----------------------------------------
; nmi_tools.asm
; ----------------------------------------

__USE_NMI_HIBASE            = 0     ; Subroutine NMI_HIBASE (1: da assemblare)
__USE_NMI_RESTORE           = 0     ; Subroutine NMI_RESTORE (1: da assemblare)

; ----------------------------------------
; print_tools.asm
; ----------------------------------------

__USE_PRINT_MSG             = 0     ; Subroutine PRINT_MSG (1: da assemblare)
__USE_PRINT_NTH             = 0     ; Subroutine PRINT_NTH (1: da assemblare; richiede PRINT_MSG)
__USE_PRINT_RAW             = 0     ; Subroutine PRINT_RAW (1: da assemblare)
__USE_PRINT_IMM             = 0     ; Subroutine PRINT_IMM (1: da assemblare)
__USE_PLOT_CHAR             = 0     ; Subroutine PLOT_CHAR (1: da assemblare; richiede COMPUTE_CELL_ADDRESS)
__USE_COLOR_CHAR            = 0     ; Subroutine COLOR_CHAR (1: da assemblare; richiede COMPUTE_CELL_ADDRESS)

; ----------------------------------------
; vic_ii_tools.asm
; ----------------------------------------

__USE_VIC_PALETTE           = 0     ; Subroutine VIC_PALETTE (1: da assemblare)
__USE_VIC_BANK              = 0     ; Subroutine VIC_BANK (1: da assemblare)
__USE_VIC_SCREEN            = 0     ; Subroutine VIC_SCREEN (1: da assemblare; richiede VIC_BANK)
__USE_VIC_CHARGEN           = 0     ; Subroutine VIC_CHARGEN (1: da assemblare; richiede VIC_BANK)
__USE_VIC_BITMAP            = 0     ; Subroutine VIC_BITMAP (1: da assemblare; richiede VIC_BANK)
__USE_VIC_COPY_CHARGEN      = 0     ; Subroutine VIC_COPY_CHARGEN (1: da assemblare; richiede VIC_CHARGEN)
__USE_COMPUTE_CELL_ADDRESS  = 0     ; Subroutine COMPUTE_CELL_ADDRESS (1: da assemblare)
__USE_GET_SCREEN_CELL       = 0     ; Subroutine GET_SCREEN_CELL (1: da assemblare; richiede COMPUTE_CELL_ADDRESS)
__USE_GET_COLOR_CELL        = 0     ; Subroutine GET_COLOR_CELL (1: da assemblare; richiede COMPUTE_CELL_ADDRESS)

; ------------------------------------------------------------------------------
; Punti di personalizzazione
; ------------------------------------------------------------------------------

__C128_C64_MODE             = 0     ; Registri e codici extra del C128 (1: da includere)
__C128_DCR                  = 0     ; Registro extra del C128DCR (1: da includere)
__DISABLE_KERNAL            = 0     ; Kernal disabilitato (1: tutta RAM; 0: Kernal attivo)
__PRESERVE_ARG              = 1     ; Macro di fp che alterano ARG (1: lo preservano; 0: no)

__BG_COL                    = $03   ; Cella in ZP: selettore del colore di sfondo ECM (0-3)
__VIC_MODEL                 = $04   ; Cella in ZP: modello di VIC-II rilevato
__KBD_HISTORY               = $05   ; Cella in ZP: serie storica di KEYSCAN
__FP_SAVED_SP               = $06   ; Cella in ZP: .S salvato prima delle chiamate alla ROM (fp)
__PUT_STRING                = $AB1E ; Subroutine di stampa di una stringa terminata da zero (STROUT)
__PUT_CHAR                  = $FFD2 ; Subroutine di stampa di un carattere (CHROUT)
