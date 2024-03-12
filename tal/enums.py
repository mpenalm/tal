from enum import Enum


class FileFormat(Enum):
    """
    File formats for NLOSCaptureData files.

    AUTODETECT
        Choose based on the file extension and contents.

    HDF5_ZNLOS
        HDF5 format used in Zaragoza-NLOS dataset
        https://graphics.unizar.es/nlos_dataset/

    HDF5_NLOS_DIRAC
        HDF5 format, deprecated

    HDF5_TAL
        HDF5 format generated by TAL (see tal render -h)

    MAT_PHASOR_FIELDS
        MAT format used in the work "Non-Line-of-Sight Imaging using Phasor Field Virtual Wave Optics"
        https://biostat.wisc.edu/~compoptics/phasornlos19/phasor_nlos_19.html

    MAT_PHASOR_FIELD_DIFFRACTION
        MAT format used in the work "Phasor Field Diffraction Based Reconstruction for Fast Non-Line-of-Sight Imaging Systems"
        https://biostat.wisc.edu/~compoptics/phasornlos20/fastnlos.html
    """
    AUTODETECT = 0
    HDF5_ZNLOS = 1
    HDF5_NLOS_DIRAC = 2
    HDF5_TAL = 3
    MAT_PHASOR_FIELDS = 4
    MAT_PHASOR_FIELD_DIFFRACTION = 5


class HFormat(Enum):
    """
    Dimensions specification for impulse response data H.

    UNKNOWN
        Avoid using this value.

    T_Sx_Sy
        H is a 3D array with dimensions (T, Sx, Sy).
        This includes confocal and non-confocal data.

    T_Lx_Ly_Sx_Sy
        H is a 5D array with dimensions (T, Lx, Ly, Sx, Sy).

    T_Si
        H is a 2D array with dimensions (T, Si).
        This includes confocal and non-confocal data.

    T_Si_Li
        H is a 3D array with dimensions (T, Si, Li).
    """
    UNKNOWN = 0
    T_Sx_Sy = 1  # confocal or not
    T_Lx_Ly_Sx_Sy = 2
    T_Si = 3  # confocal or not
    T_Li_Si = 4

    def time_dim(self) -> int:
        """ Returns the index of the time (T) dimension. """
        assert self in [HFormat.T_Sx_Sy,
                        HFormat.T_Lx_Ly_Sx_Sy,
                        HFormat.T_Si,
                        HFormat.T_Li_Si], \
            f'Unexpected HFormat {self}'
        return 0


class GridFormat(Enum):
    """
    Dimensions specification for grid data.

    UNKNOWN
        Avoid using this value.

    N_3
        Grid is a 2D array with dimensions (N, 3).
        Prefer more specific formats (e.g. X_Y_3) if your data
        is in fact a 2D grid of points, there are some functions
        that optimize this fact.

    X_Y_3
        Grid is a 3D array with dimensions (X, Y, 3).
    """
    UNKNOWN = 0
    N_3 = 1
    X_Y_3 = 2


class VolumeFormat(Enum):
    """
    Dimensions specification for volume data.

    UNKNOWN
        Avoid using this value. Some implementations of the
        reconstruction algorithms will guess your volume format
        based on the data that you pass to it, but it is better
        to be explicit.

    N_3
        Volume is a 2D array with dimensions (N, 3).
        Prefer more specific formats (e.g. X_Y_3, X_Y_Z_3) if your data
        is in fact a 2D/3D set of points, there are some functions
        that optimize this fact.

    X_Y_Z_3
        Volume is a 4D array with dimensions (X, Y, Z, 3).

    X_Y_3
        Volume is a 3D array with dimensions (X, Y, 3).
    """
    UNKNOWN = 0
    N_3 = 1
    X_Y_Z_3 = 2
    X_Y_3 = 3

    def xyz_dim_is_last(self) -> bool:
        assert self in [VolumeFormat.N_3,
                        VolumeFormat.X_Y_Z_3,
                        VolumeFormat.X_Y_3]
        return True


class CameraSystem(Enum):
    """
    Reconstruction algorithms work as a virtual camera system.
    This camera system can focus at different points of the hidden scene,
    and virtually illuminate other points. The camera system chosen chooses
    the behaviour of the virtual camera.

    For more info., read the supplementary material of the paper
    "Non-Line-of-Sight Imaging using Phasor Field Virtual Wave Optics"
    https://biostat.wisc.edu/~compoptics/phasornlos19/phasor_nlos_19.html
    (section A and Tables S.2 and S.3)

    The projector cameras are implemented as described in "Virtual light
    transport matrices for non-line-of-sight imaging"
    https://webdiis.unizar.es/~juliom/pubs/2021ICCV-NLOSvLTM/2021ICCV_NLOSvLTM.pdf

    DIRECT_LIGHT
        Confocal camera at t = 0. Most common NLOS reconstruction system.

    CONFOCAL_TIME_GATED
        Confocal camera with time gating. Computes a video of the scene (t >= 0).
        The returned reconstruction will have an extra time dimension.

    TRANSIENT
        Transient camera. Computes a video of the scene (t >= 0).
        The returned reconstruction will have an extra time dimension.

    PROJECTOR_CAMERA
        Projector camera. If you have multiple illumination points in your data,
        this camera system will focus the illumination to a point in the hidden
        volume.

    PROJECTOR_CAMERA_T0
        Projector camera at t = 0.
    """
    DIRECT_LIGHT = 0  # evaluate confocal time gated at t=0
    CONFOCAL_TIME_GATED = 1  # pulsed focused light
    PROJECTOR_CAMERA = 2  # focus the illumination aperture to a point
    PROJECTOR_CAMERA_T0 = 3  # evaluate projector camera at t=0
    TRANSIENT = 4  # pulsed point light
    TRANSIENT_T0 = 5  # evaluate transient at t=0
    # STEADY_STATE = 6  # NYI (integrate transient over time), also add to functions below
    # PHOTO_CAMERA = 7  # NYI (single-freq imaging), also add to functions below

    def bp_accounts_for_d_2(self) -> bool:
        return self in [CameraSystem.DIRECT_LIGHT,
                        CameraSystem.PROJECTOR_CAMERA,
                        CameraSystem.PROJECTOR_CAMERA_T0,
                        CameraSystem.CONFOCAL_TIME_GATED]

    def is_transient(self) -> bool:
        return self in [CameraSystem.TRANSIENT,
                        CameraSystem.CONFOCAL_TIME_GATED,
                        CameraSystem.PROJECTOR_CAMERA]

    def implements_projector(self) -> bool:
        return self in [CameraSystem.PROJECTOR_CAMERA,
                        CameraSystem.PROJECTOR_CAMERA_T0]
